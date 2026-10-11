"""Small-catalogue implicit recommendation with chronological evaluation."""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def fit_recommender(history, alpha=0.5):
    catalogue = history.groupby('name').agg(place=('place', 'first'), price=('price', 'median'), bookings=('name', 'size')).sort_index()
    counts = pd.crosstab(history.userCode, history['name']).reindex(columns=catalogue.index, fill_value=0)
    similarity = cosine_similarity(np.log1p(counts.to_numpy()).T)
    np.fill_diagonal(similarity, 0)
    return {'catalogue': catalogue, 'counts': counts, 'similarity': similarity, 'alpha': alpha}


def scores(bundle, user_code=None, method='hybrid'):
    catalogue, counts = bundle['catalogue'], bundle['counts']
    popular = catalogue.bookings.to_numpy(dtype=float)
    popular /= popular.sum()
    if method == 'popularity' or user_code not in counts.index:
        return popular, 'booking popularity (no training history for this user)' if user_code not in counts.index else 'booking popularity'
    own = counts.loc[user_code].to_numpy(dtype=float)
    own /= own.sum()
    related = own @ bundle['similarity']
    related = related / related.sum() if related.sum() else popular
    personal = 0.8 * own + 0.2 * related
    alpha = bundle['alpha']
    return alpha * personal + (1 - alpha) * popular, 'past booking frequency and similar hotel interactions'


def recommend(bundle, user_code=None, destination=None, budget=None, k=3, method='hybrid'):
    values, reason = scores(bundle, user_code, method)
    result = bundle['catalogue'].copy()
    result['score'] = values
    if destination:
        result = result[result.place == destination]
    if budget is not None:
        result = result[result.price <= budget]
    result = result.sort_values(['score', 'bookings'], ascending=False).head(k).reset_index()
    result['reason'] = reason
    result = result.rename(columns={'name': 'hotel', 'price': 'historical_nightly_price'})
    return result.to_dict('records')


def evaluate_recommender(bundle, future, method='hybrid', k=3):
    """Macro-average per-user unique relevant items; repeat bookings remain eligible."""
    recalls, ndcgs, covered = [], [], set()
    catalogue = set(bundle['catalogue'].index)
    unknown = 0
    for user, events in future.groupby('userCode'):
        relevant = set(events['name'])
        unknown += len(relevant - catalogue)
        ranking = [r['hotel'] for r in recommend(bundle, int(user), k=k, method=method)]
        hits = [int(x in relevant) for x in ranking]
        recalls.append(sum(hits) / len(relevant))
        dcg = sum(hit / np.log2(i + 2) for i, hit in enumerate(hits))
        ideal = sum(1 / np.log2(i + 2) for i in range(min(k, len(relevant))))
        ndcgs.append(dcg / ideal if ideal else 0)
        covered.update(ranking)
    return {'recall_at_3': float(np.mean(recalls)), 'ndcg_at_3': float(np.mean(ndcgs)),
            'coverage': len(covered) / len(catalogue), 'evaluated_users': len(recalls),
            'unknown_relevant_items': unknown}
