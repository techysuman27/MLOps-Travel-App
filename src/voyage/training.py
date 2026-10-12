"""Reproducible candidates, independent holdouts, and complete MLflow artifacts."""
import json
import os
import platform
import subprocess
import time
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, classification_report,
                             confusion_matrix, f1_score, mean_absolute_error, r2_score, root_mean_squared_error)
from sklearn.model_selection import train_test_split

from voyage.artifacts import save_bundle, write_json
from voyage.data import chronological_split, load_data, sha256
from voyage.features import CATEGORIES, FLIGHT_INPUTS, classification_pipeline, flight_pipeline
from voyage.recommendation import evaluate_recommender, fit_recommender


def regression_metrics(y, prediction):
    return {'mae': float(mean_absolute_error(y, prediction)),
            'rmse': float(root_mean_squared_error(y, prediction)), 'r2': float(r2_score(y, prediction))}


def class_metrics(y, prediction):
    return {'accuracy': float(accuracy_score(y, prediction)),
            'balanced_accuracy': float(balanced_accuracy_score(y, prediction)),
            'macro_f1': float(f1_score(y, prediction, average='macro', zero_division=0))}


def train_flights(df):
    train, valid, test, split = chronological_split(df, group_trips=True)
    estimators = {
        'median_baseline': DummyRegressor(strategy='median'),
        'ridge': Ridge(alpha=10),
        'hist_gradient_100': HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=31, early_stopping=False, random_state=42),
        'hist_gradient_200': HistGradientBoostingRegressor(max_iter=200, max_leaf_nodes=31, early_stopping=False, random_state=42),
    }
    candidates = []
    for name, estimator in estimators.items():
        start = time.perf_counter()
        pipeline = flight_pipeline(estimator).fit(train[FLIGHT_INPUTS], train.price)
        metrics = regression_metrics(valid.price, pipeline.predict(valid[FLIGHT_INPUTS]))
        candidates.append({'model': name, **metrics, 'fit_seconds': time.perf_counter() - start})
        print(name, metrics, flush=True)
    selected = min(candidates, key=lambda row: row['rmse'])['model']
    baseline_rmse = candidates[0]['rmse']
    best = next(row for row in candidates if row['model'] == selected)
    passed = best['rmse'] < 0.90 * baseline_rmse
    combined = pd.concat([train, valid])
    pipeline = flight_pipeline(clone(estimators[selected])).fit(combined[FLIGHT_INPUTS], combined.price)
    prediction = pipeline.predict(test[FLIGHT_INPUTS])
    baseline = flight_pipeline(DummyRegressor(strategy='median')).fit(combined[FLIGHT_INPUTS], combined.price)
    baseline_test = regression_metrics(test.price, baseline.predict(test[FLIGHT_INPUTS]))
    residuals = test[['from', 'to', 'flightType', 'price']].copy()
    residuals['absolute_error'] = np.abs(test.price - prediction)
    slices = residuals.groupby(['from', 'to', 'flightType']).agg(n=('price', 'size'), mae=('absolute_error', 'mean')).reset_index()
    report = {'selected': selected, 'split': split, 'validation_candidates': candidates,
              'test_metrics': regression_metrics(test.price, prediction), 'test_baseline': baseline_test,
              'error_slices': slices.to_dict('records'),
              'quality_gate': {'passed': bool(passed), 'rule': 'Validation RMSE at least 10% below median baseline'},
              'limitations': ['Historical dataset; not live fares.', 'Currency is unspecified by the provided schema.',
                              'No booking lead time is available; date is used only as recorded.']}
    meta = {'categories': {c: sorted(combined[c].unique().tolist()) for c in CATEGORIES},
            'numeric_ranges': {c: [float(combined[c].min()), float(combined[c].max())] for c in ['time', 'distance']},
            'training_date_max': str(combined.date.max().date())}
    return {'pipeline': pipeline, 'metadata': meta}, report, test[FLIGHT_INPUTS].head(3)


def train_classification(df):
    train, remaining = train_test_split(df, test_size=0.30, stratify=df.gender, random_state=42)
    valid, test = train_test_split(remaining, test_size=0.5, stratify=remaining.gender, random_state=42)
    features = ['company', 'age']
    estimators = {'majority_baseline': DummyClassifier(strategy='most_frequent'),
                  'logistic': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
                  'random_forest': RandomForestClassifier(n_estimators=120, max_depth=5, min_samples_leaf=10, class_weight='balanced', random_state=42, n_jobs=2)}
    candidates = []
    for name, estimator in estimators.items():
        pipeline = classification_pipeline(estimator).fit(train[features], train.gender)
        candidates.append({'model': name, **class_metrics(valid.gender, pipeline.predict(valid[features]))})
    selected = max(candidates, key=lambda row: row['macro_f1'])['model']
    combined = pd.concat([train, valid])
    pipeline = classification_pipeline(clone(estimators[selected])).fit(combined[features], combined.gender)
    prediction = pipeline.predict(test[features])
    baseline = classification_pipeline(DummyClassifier(strategy='most_frequent')).fit(combined[features], combined.gender)
    labels = list(pipeline.classes_)
    report = {'selected': selected, 'validation_candidates': candidates,
              'split': {'train_rows': len(train), 'validation_rows': len(valid), 'test_rows': len(test), 'strategy': 'stratified users; seed 42'},
              'test_metrics': class_metrics(test.gender, prediction),
              'test_baseline': class_metrics(test.gender, baseline.predict(test[features])),
              'classification_report': classification_report(test.gender, prediction, output_dict=True, zero_division=0),
              'confusion_matrix': confusion_matrix(test.gender, prediction, labels=labels).tolist(), 'labels': labels,
              'quality_gate': {'passed': True, 'rule': 'Educational benchmark only; no business decision or identity inference'},
              'limitations': ['none is an undocumented source category, not an inferred identity.',
                              'Only company and age are used; identifiers and personal names are excluded.',
                              'Limited accuracy is expected and must be reported without exaggeration.']}
    return {'pipeline': pipeline, 'metadata': {'companies': sorted(df.company.unique().tolist()), 'labels': labels}}, report, test[features].head(3)


def train_hotels(df):
    train, valid, test, split = chronological_split(df)
    candidates = []
    for alpha in [0.0, 0.5, 1.0]:
        model = fit_recommender(train, alpha)
        candidates.append({'model': f'hybrid_alpha_{alpha}', 'alpha': alpha, **evaluate_recommender(model, valid)})
    selected = max(candidates, key=lambda row: row['ndcg_at_3'])
    model = fit_recommender(pd.concat([train, valid]), selected['alpha'])
    report = {'selected': selected['model'], 'split': split, 'validation_candidates': candidates,
              'test_metrics': evaluate_recommender(model, test), 'test_baseline': evaluate_recommender(model, test, method='popularity'),
              'quality_gate': {'passed': True, 'rule': 'Select validation NDCG@3; popularity is an eligible fallback'},
              'limitations': ['Nine hotels and one hotel per destination; no real-time availability.',
                              'Bookings are implicit signals, not ratings. Previously booked hotels remain eligible.',
                              'Macro per-user unique-item Recall@3 and NDCG@3; catalogue is training-period only.']}
    return model, report, None


def run_training(task, data_dir='data/raw', model_dir='models', reports_dir='reports', tracking_uri=None):
    frames = load_data(data_dir)
    mapping = {'flights': train_flights, 'classification': train_classification, 'hotels': train_hotels}
    source = 'users' if task == 'classification' else task
    uri = tracking_uri or os.environ.get('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db')
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(f'voyage-{task}')
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = 'unavailable', True
    with mlflow.start_run(run_name=f'{task}-candidate') as run:
        model, report, example = mapping[task](frames[source])
        report.update({'data_sha256': sha256(Path(data_dir) / f'{source}.csv'), 'git_commit': commit,
                       'working_tree_dirty': dirty, 'python_version': platform.python_version()})
        mlflow.log_params({'selected': report['selected'], 'seed': 42, 'data_sha256': report['data_sha256'], 'git_commit': commit})
        mlflow.set_tags({'working_tree_dirty': str(dirty), 'task': task})
        for row in report['validation_candidates']:
            with mlflow.start_run(run_name=row['model'], nested=True):
                mlflow.log_param('candidate', row['model'])
                mlflow.log_metrics({f'validation_{k}': float(v) for k, v in row.items() if isinstance(v, (int, float))})
        mlflow.log_metrics({f'test_{k}': float(v) for k, v in report['test_metrics'].items()})
        if example is not None:
            example = example.copy()
            if 'date' in example:
                example['date'] = example.date.dt.strftime('%Y-%m-%d')
            mlflow.sklearn.log_model(model['pipeline'], name='pipeline', input_example=example,
                                    serialization_format='cloudpickle', code_paths=[str(Path(__file__).resolve().parent)],
                                    registered_model_name=f'voyage-{task}' if report['quality_gate']['passed'] else None)
        manifest = save_bundle(task, model, report, run.info.run_id, model_dir)
        mlflow.log_artifact(str(Path(model_dir) / manifest['artifact']), artifact_path='bundle')
        mlflow.log_dict(report, 'evaluation.json')
        write_json(Path(reports_dir) / f'{task}.json', report)
        print(json.dumps({'task': task, 'version': run.info.run_id, 'selected': report['selected'], 'test_metrics': report['test_metrics'], 'quality_gate': report['quality_gate']}, indent=2), flush=True)
    return manifest
