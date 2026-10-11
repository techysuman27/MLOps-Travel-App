"""Create original Colab notebooks following the supplied template sections."""
import json
from pathlib import Path
import textwrap

REPO = 'https://github.com/techysuman27/MLOps-Travel-App'


def markdown(text):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': textwrap.dedent(text).strip().splitlines(True)}


def code(text):
    return {'cell_type': 'code', 'metadata': {}, 'source': textwrap.dedent(text).strip().splitlines(True), 'execution_count': None, 'outputs': []}


TASKS = {
    'flights': ('01_Flight_Price_Regression.ipynb', 'Flight Price Regression', 'Regression',
                'Estimate historical flight prices from route, cabin, agency, duration, distance and date. Predictions are dataset-unit estimates, not live fares.',
                'Price errors affect budgeting. MAE expresses typical absolute error; RMSE emphasizes large mistakes; R-squared compares residual variation with target variation.'),
    'classification': ('02_Gender_Label_Classification.ipynb', 'Educational Gender-Label Classification', 'Classification',
                       'Test whether age and company contain predictive information about recorded labels. The undocumented label none is retained, while personal names and identifier code are excluded. Results are an educational benchmark and must not be treated as identity inference.',
                       'Macro F1 gives each source label equal weight; balanced accuracy averages per-class recall. A majority baseline prevents misleading claims based only on raw accuracy.'),
    'hotels': ('03_Hotel_Recommendation.ipynb', 'Hotel and Destination Recommendation', 'Recommendation',
               'Rank the nine historical hotel/destination options using booking popularity and past implicit interactions. Each destination has only one hotel, so filtering to a city is catalogue lookup rather than a competitive within-city ranking.',
               'Recall@3 measures the fraction of future distinct booked hotels retrieved. NDCG@3 rewards relevant hotels nearer the top. Coverage measures variety across recommendations; with nine hotels, large K can make results look deceptively good.'),
}


def build(task, spec):
    filename, title, project_type, summary, metrics_reason = spec
    cells = [markdown(f'''# Voyage Analytics — {title}
    **Project type:** {project_type}  
    **Contribution:** Individual  
    **Author:** techysuman27 (replace with your preferred submission name if needed)

    # Project Summary
    {summary}

    This notebook provides the assessed modeling narrative. The shared package implements repeatable training and preprocessing used by Flask and Airflow as well. MLflow captures the experiment; Docker, Kubernetes and Jenkins belong to the accompanying repository. Measured outputs below come from this dataset and must not be described as real-world travel-market performance.

    # GitHub Link
    {REPO}

    # Problem Statement
    {summary}

    # General Guidelines
    Follow the supplied template's eight main sections. This original notebook contains fifteen training-only visualizations, with reasons, measured observations and business implications. The test partition is reserved for final evaluation. Run all cells in order. The initial bootstrap may require network access in Colab.
    '''), code(f'''
    import os, sys, subprocess
    from pathlib import Path
    os.environ['OMP_NUM_THREADS'] = '4'
    os.environ['MLFLOW_DISABLE_AGENT_HINT'] = '1'
    IN_COLAB = 'google.colab' in sys.modules
    if IN_COLAB:
        root = Path('/content/MLOps-Travel-App')
        if not root.exists():
            subprocess.run(['git', 'clone', '{REPO}.git', str(root)], check=True)
        os.chdir(root)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--no-deps', '.'], check=True)
    else:
        root = Path.cwd()
        if root.name == 'notebooks': root = root.parent
        os.chdir(root)
        sys.path.insert(0, str(root / 'src'))
    if not Path('data/raw/flights.csv').exists():
        subprocess.run([sys.executable, 'scripts/download_data.py'], check=True)
    TASK = '{task}'
    print('Repository:', root)
    '''), markdown('## 1. Know Your Data\n### Import Libraries and Dataset Loading'), code('''
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from IPython.display import display, Image
    from io import BytesIO
    from sklearn.model_selection import train_test_split
    from voyage.data import load_data, chronological_split, sha256
    from voyage.exploration import draw_chart
    from voyage.training import run_training
    from voyage.artifacts import load_bundle, promote
    frames = load_data('data/raw')
    df = frames['users' if TASK == 'classification' else TASK]
    print('Rows and columns:', df.shape)
    display(df.drop(columns=['name'], errors='ignore').head())
    display(pd.DataFrame({'dtype': df.dtypes.astype(str), 'missing': df.isna().sum(), 'unique': df.nunique()}))
    print('Exact duplicates:', df.duplicated().sum())
    '''), markdown('''### What did we learn about the dataset?
    Validation checks the required columns, numeric values, dates and user references. No empty fields or exact duplicate rows were found in the initial source audit. This does not establish representativeness or real-world validity. A travel/user pair has two flight legs; hotel totals must not be summed after an unrestricted flight join.
    '''), markdown('## 2. Understanding Your Variables'), code('''
    descriptions = {
        'travelCode': 'Trip identifier; grouping and linkage only', 'userCode': 'User reference; history and linkage only',
        'code': 'User identifier; excluded from classification features', 'from': 'Recorded origin', 'to': 'Recorded destination',
        'flightType': 'Recorded cabin category', 'price': 'Flight price or hotel nightly price, according to table',
        'time': 'Recorded flight duration', 'distance': 'Recorded flight distance; units unverified',
        'agency': 'Recorded agency', 'date': 'Recorded travel/booking date', 'name': 'User name or hotel name, according to table',
        'place': 'Hotel destination', 'days': 'Stay duration', 'total': 'Nightly price times stay duration',
        'company': 'Associated company', 'gender': 'Source label: male, female, none; none is undocumented', 'age': 'Recorded user age'
    }
    display(pd.DataFrame({'variable': df.columns, 'meaning': [descriptions[c] for c in df.columns]}))
    '''), markdown('## 3. Data Wrangling'), code('''
    if TASK == 'classification':
        train, rest = train_test_split(df, test_size=.30, stratify=df.gender, random_state=42)
        valid, test = train_test_split(rest, test_size=.5, stratify=rest.gender, random_state=42)
        split = {'train': len(train), 'validation': len(valid), 'test': len(test)}
        assert set(train.code).isdisjoint(test.code)
    else:
        train, valid, test, split = chronological_split(df, group_trips=TASK == 'flights')
        assert train.date.max() < valid.date.min() < test.date.min()
    display(split)
    eda = train.copy()
    '''), markdown('''### Manipulations and reasoning
    Source dates are parsed explicitly. Numerical contract violations stop execution instead of being silently filled. There is no need to impute this complete source snapshot. Exploration below uses only the training partition. Flight trips crossing time boundaries are purged. For users, stratification preserves label representation while keeping each user in one partition. For hotels, future interactions remain held out and repeat bookings stay eligible.
    '''), markdown('## 4. Data Visualization, Storytelling and Experimenting with Charts')]
    for i in range(15):
        cells.extend([markdown(f'''### Chart {i+1}
        **Why this chart?** {'A distribution, group comparison or relationship plot exposes the support and variation relevant to this task. Counts and proportions help distinguish common patterns from thinly represented cases.'}
        '''), code(f'''
        figure, observed_insight = draw_chart(TASK, {i}, eda)
        image_buffer = BytesIO()
        figure.savefig(image_buffer, format='png', dpi=110, bbox_inches='tight')
        display(Image(data=image_buffer.getvalue()))
        plt.close(figure)
        print('Observed insight:', observed_insight)
        '''), markdown('''**Business implication:** Use the measured observation to guide feature checks, coverage limits and evaluation slices. It can support budgeting or catalogue exploration, but it is not proof of a causal effect or increased business revenue. Sparse groups and historical patterns can produce poor generalization; the independent holdout checks this separately.
        ''')])
    cells.append(markdown('''## 5. Hypothesis Testing
    These are exploratory checks on training data only, using three comparisons and a Bonferroni significance level of 0.05/3. Statistical association does not establish practical predictive value. Flight/hotel records repeat users and trips, so the tests use one observation per user to reduce within-user dependence; remaining observational confounding limits interpretation.
    '''))
    cells.append(code('''
    from scipy.stats import kruskal, chi2_contingency, spearmanr
    independent = eda.drop_duplicates('code' if TASK == 'classification' else 'userCode')
    tests = []
    if TASK == 'flights':
        for category in ['flightType', 'agency']:
            groups = [group.price.to_numpy() for _, group in independent.groupby(category)]
            statistic, p = kruskal(*groups)
            tests.append((f'H0: price distributions are equal across {category}', statistic, p))
        statistic, p = spearmanr(independent.distance, independent.price)
        tests.append(('H0: distance and price have zero rank association', statistic, p))
    elif TASK == 'classification':
        statistic, p, dof, expected = chi2_contingency(pd.crosstab(independent.company, independent.gender))
        tests.append(('H0: company and source label are independent', statistic, p))
        print('Minimum expected count for company/label chi-square:', expected.min())
        statistic, p = kruskal(*[group.age.to_numpy() for _, group in independent.groupby('gender')])
        tests.append(('H0: age distributions are equal across labels', statistic, p))
        statistic, p = kruskal(*[group.age.to_numpy() for _, group in independent.groupby('company')])
        tests.append(('H0: age distributions are equal across companies', statistic, p))
    else:
        statistic, p = kruskal(*[group.days.to_numpy() for _, group in independent.groupby('place')])
        tests.append(('H0: stay distributions are equal across destinations', statistic, p))
        statistic, p = spearmanr(independent.days, independent.total)
        tests.append(('H0: stay duration and total have zero rank association', statistic, p))
        statistic, p = spearmanr(independent.price, independent.days)
        tests.append(('H0: nightly price and duration have zero rank association', statistic, p))
    hypothesis_results = pd.DataFrame(tests, columns=['null_hypothesis', 'statistic', 'p_value'])
    hypothesis_results['decision'] = np.where(hypothesis_results.p_value < .05 / 3, 'Reject H0 (exploratory)', 'Do not reject H0')
    display(hypothesis_results)
    '''))
    cells.extend([markdown('''### Test selection and limitations
    Kruskal–Wallis compares group distributions without assuming normality; unequal distribution shapes can complicate a median-only interpretation. Spearman measures monotonic association. Chi-square tests categorical independence; inspect its expected counts before relying on the approximation. A small p-value is not an effect-size estimate. The hotel total is arithmetically related to days and nightly price, so that association is expected and cannot establish causality.

    ## 6. Feature Engineering and Data Pre-processing
    **Missing values:** none are silently imputed; invalid source inputs fail the contract.  
    **Outliers:** no arbitrary price truncation. Valid extremes stay in evaluation; boxplots hide fliers only for readability.  
    **Categorical encoding:** one-hot encoding is fitted inside training pipelines. The API rejects unknown flight categories.  
    **Text preprocessing:** not applicable; we exclude personal names and do not invent review text.  
    **Feature manipulation:** flight month and weekday come from the same serialized transformer during training and serving.  
    **Feature selection:** identifiers and target-derived columns are excluded. Hotel identifiers are items, not numeric scores.  
    **Scaling:** numeric flight features and age use training-fitted standardization; hotel interaction counts are normalized in the recommendation model.  
    **Dimensionality reduction:** unnecessary for the small feature space/catalogue.  
    **Splitting:** chronological partitions for event tasks and stratified user partitions for classification.  
    **Imbalance:** compare the classification baseline and balanced candidates using macro/per-label metrics, with no pre-split oversampling.

    ## 7. ML Model Implementation
    Candidate definitions are in `src/voyage/training.py`. The following call trains candidates, selects using validation metrics, refits the winner on training plus validation, evaluates it on the final test partition and logs the result to MLflow. Training is deliberately shared with the production workflow. The notebook does not maintain a second, divergent implementation.
    '''), code('''
    # Set True for a fresh full training run. Saved execution uses the verified
    # report/artifact when present to avoid repeating final-test selection.
    REBUILD_MODELS = False
    import json
    report_path = Path('reports') / f'{TASK}.json'
    if REBUILD_MODELS or not report_path.exists():
        run_training(TASK)
        promote(TASK)
    report = json.loads(report_path.read_text(encoding='utf-8'))
    candidates = pd.DataFrame(report['validation_candidates'])
    display(candidates)
    print('Selected:', report['selected'])
    print('Selection gate:', report['quality_gate'])
    '''), markdown('''### Model comparison and tuning
    Regression compares a median baseline, Ridge, and two histogram-gradient-boosting iteration budgets. Classification compares a majority baseline, balanced logistic regression and a depth-limited random forest. Recommendation compares popularity (alpha=0) with two personalization weights. This is a bounded validation search, not nested cross-validation; no claim of exhaustive tuning is made. Preprocessing is fitted on training observations for each candidate. The final test results never determine which candidate wins.
    '''), code('''
    score = 'rmse' if TASK == 'flights' else ('macro_f1' if TASK == 'classification' else 'ndcg_at_3')
    ax = candidates.set_index('model')[score].plot.bar(title='Validation comparison')
    ax.set_ylabel(score)
    plt.tight_layout()
    image_buffer = BytesIO()
    ax.figure.savefig(image_buffer, format='png', dpi=110, bbox_inches='tight')
    display(Image(data=image_buffer.getvalue()))
    plt.close(ax.figure)
    display(pd.DataFrame({'selected_model': report['test_metrics'], 'baseline': report['test_baseline']}))
    if TASK == 'classification':
        display(pd.DataFrame(report['classification_report']).T)
        display(pd.DataFrame(report['confusion_matrix'], index=report['labels'], columns=report['labels']))
    if TASK == 'flights':
        display(pd.DataFrame(report['error_slices']).sort_values('mae', ascending=False).head(10))
    '''), markdown(f'''### Evaluation, business meaning and model choice
    {metrics_reason}

    The table shows whether personalization or a learned classifier actually improves on its baseline. A weak or negative result must stay in the report. Very high flight accuracy on this constrained historical catalogue does not imply comparable live-market accuracy. Analyze route/cabin slices and report their sample sizes. For classification, inspect each label rather than implying aggregate accuracy applies equally to everyone. Recommendation evaluation concerns held-out observed bookings, not user satisfaction.

    ### Explainability
    Use the following held-out permutation check for predictive models; it measures score changes under input permutation and may understate correlated features. For recommendations, inspect the actual popularity/history signals. Neither explanation establishes causality.
    '''), code('''
    bundle, manifest = load_bundle(TASK)
    if TASK != 'hotels':
        from sklearn.inspection import permutation_importance
        feature_names = ['company', 'age'] if TASK == 'classification' else ['from', 'to', 'flightType', 'agency', 'time', 'distance', 'date']
        sample = test.sample(min(500, len(test)), random_state=42)
        target = sample.gender if TASK == 'classification' else sample.price
        scoring = 'f1_macro' if TASK == 'classification' else 'neg_mean_absolute_error'
        explanation = permutation_importance(bundle['pipeline'], sample[feature_names], target, n_repeats=3, random_state=42, scoring=scoring)
        display(pd.DataFrame({'feature': feature_names, 'importance': explanation.importances_mean}).sort_values('importance', ascending=False))
    else:
        from voyage.recommendation import recommend
        display(pd.DataFrame(recommend(bundle, user_code=0, k=3)))
    '''), markdown('''## 8. Future Work and Deployment Artifact
    The complete pipeline or recommendation bundle is saved as joblib with a SHA-256 manifest. A separate promotion operation only approves passing candidates; failed candidates preserve the current release. The Flask app loads the exact same artifact at startup. MLflow records the experiment and bundle. Kubernetes/Jenkins deployment evidence is maintained separately and must not be inferred merely from a configuration file.
    '''), code('''
    print('Verified version:', manifest['version'])
    print('Artifact:', manifest['artifact'])
    print('Checksum:', manifest['sha256'])
    if TASK != 'hotels':
        sample = test.head(3)
        display(bundle['pipeline'].predict(sample[feature_names]))
    else:
        display(pd.DataFrame(recommend(bundle, user_code=999999, k=3)))
    '''), markdown('''# Conclusion
    This notebook connects data understanding, partition design, modeling, evaluation and a reproducible serving artifact. Read the measured comparison above before claiming any improvement. Future work includes newer independently sourced records, better documented field semantics, stronger temporal robustness checks and actual outcome feedback. Recommendation improvements require a richer catalogue. Classification remains an educational source-label benchmark with limited business relevance.

    The repository contains the API, Streamlit application, infrastructure and workflow code. The submission documentation must distinguish stages that ran successfully from stages still awaiting hosting or account setup.
    ''')])
    nb = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                                      'language_info': {'name': 'python'}, 'colab': {'name': filename}}, 'nbformat': 4, 'nbformat_minor': 5}
    # Stable IDs support notebook tooling and clean diffs.
    for i, cell in enumerate(cells): cell['id'] = f'{task}-{i:03}'
    Path('notebooks').mkdir(exist_ok=True)
    Path('notebooks', filename).write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    for task, spec in TASKS.items(): build(task, spec)
