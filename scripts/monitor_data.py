"""Historical distribution comparison, explicitly not an accuracy monitor."""
import numpy as np
from voyage.data import load_data, chronological_split
from voyage.artifacts import write_json

frames = load_data()
train, _, test, split = chronological_split(frames['flights'], group_trips=True)
results = {}
for column in ['time', 'distance']:
    inner = np.unique(np.quantile(train[column], np.linspace(.1, .9, 9)))
    bins = np.r_[-np.inf, inner, np.inf]
    expected = np.histogram(train[column], bins=bins)[0] / len(train)
    observed = np.histogram(test[column], bins=bins)[0] / len(test)
    expected, observed = np.clip(expected, 1e-6, 1), np.clip(observed, 1e-6, 1)
    results[column] = {'psi': float(np.sum((observed - expected) * np.log(observed / expected)))}
for column in ['from', 'to', 'flightType', 'agency']:
    categories = sorted(set(train[column]) | set(test[column]))
    a = train[column].value_counts(normalize=True).reindex(categories, fill_value=0)
    b = test[column].value_counts(normalize=True).reindex(categories, fill_value=0)
    results[column] = {'total_variation_distance': float(.5 * (a - b).abs().sum())}
report = {'scope': 'Historical train versus held-out period; not live traffic or predictive accuracy',
          'split': split, 'features': results, 'interpretation': 'Investigate distribution changes. Accuracy requires actual outcomes and cannot be inferred from drift alone.'}
write_json('reports/drift.json', report)
print(report)
