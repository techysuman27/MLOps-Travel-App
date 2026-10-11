"""The same date transformation is serialized with the flight estimator."""
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FLIGHT_INPUTS = ['from', 'to', 'flightType', 'agency', 'time', 'distance', 'date']
CATEGORIES = ['from', 'to', 'flightType', 'agency']
NUMERICS = ['time', 'distance', 'month', 'weekday']


class FlightFeatures(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        result = X[FLIGHT_INPUTS].copy()
        date = pd.to_datetime(result.pop('date'), errors='raise')
        result['month'] = date.dt.month
        result['weekday'] = date.dt.dayofweek
        return result


def flight_pipeline(estimator):
    preprocessing = ColumnTransformer([
        ('category', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORIES),
        ('numeric', StandardScaler(), NUMERICS),
    ])
    return Pipeline([('calendar', FlightFeatures()), ('preprocessing', preprocessing), ('model', estimator)])


def classification_pipeline(estimator):
    preprocessing = ColumnTransformer([
        ('company', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['company']),
        ('age', StandardScaler(), ['age']),
    ])
    return Pipeline([('preprocessing', preprocessing), ('model', estimator)])
