import json
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import Ridge
from voyage.data import chronological_split
from voyage.features import flight_pipeline, FLIGHT_INPUTS
from voyage.artifacts import load_bundle, promote, save_bundle
from voyage.recommendation import fit_recommender, recommend, evaluate_recommender
from api.app import create_app


def flight_frame():
    rows = []
    for trip in range(60):
        for offset in [0, 3]:
            rows.append({'travelCode': trip, 'userCode': trip % 5, 'from': 'A', 'to': 'B',
                         'flightType': 'economic', 'agency': 'Agency', 'time': 2.0, 'distance': 500.,
                         'date': pd.Timestamp('2021-01-01') + pd.Timedelta(days=trip * 2 + offset), 'price': 200 + trip})
    return pd.DataFrame(rows)


def test_time_split_purges_cross_boundary_trips():
    train, valid, test, info = chronological_split(flight_frame(), group_trips=True)
    assert train.date.max() < valid.date.min() < test.date.min()
    assert set(train.travelCode).isdisjoint(valid.travelCode)
    assert set(valid.travelCode).isdisjoint(test.travelCode)
    assert info['purged_rows'] > 0


def test_serialized_pipeline_preserves_prediction(tmp_path):
    df = flight_frame()
    pipeline = flight_pipeline(Ridge()).fit(df[FLIGHT_INPUTS], df.price)
    report = {'quality_gate': {'passed': True}}
    save_bundle('flights', {'pipeline': pipeline}, report, 'test-run', tmp_path)
    promote('flights', tmp_path)
    restored, manifest = load_bundle('flights', tmp_path)
    np.testing.assert_allclose(restored['pipeline'].predict(df[FLIGHT_INPUTS]), pipeline.predict(df[FLIGHT_INPUTS]))
    (tmp_path / manifest['artifact']).write_bytes(b'corrupted')
    with pytest.raises(ValueError, match='integrity'):
        load_bundle('flights', tmp_path)


def test_failed_candidate_preserves_active_version(tmp_path):
    save_bundle('flights', {}, {'quality_gate': {'passed': True}}, 'good', tmp_path)
    promote('flights', tmp_path)
    save_bundle('flights', {}, {'quality_gate': {'passed': False}}, 'bad', tmp_path)
    with pytest.raises(ValueError, match='quality gate'):
        promote('flights', tmp_path)
    assert json.loads((tmp_path / 'flights.json').read_text())['version'] == 'good'


def test_missing_models_not_ready(tmp_path):
    client = create_app(tmp_path, tmp_path).test_client()
    assert client.get('/health/live').status_code == 200
    assert client.get('/health/ready').status_code == 503
    assert client.post('/api/v1/flights/predict', json={}).status_code == 503


def test_hotel_cold_start_and_filters():
    data = pd.DataFrame({'userCode': [1, 1, 2, 2], 'name': ['One', 'One', 'Two', 'One'],
                         'place': ['A', 'A', 'B', 'A'], 'price': [100, 100, 250, 100]})
    bundle = fit_recommender(data)
    assert recommend(bundle, 999)[0]['hotel'] == 'One'
    assert recommend(bundle, 999, destination='B', budget=200) == []
    assert recommend(bundle, 1, destination='B')[0]['hotel'] == 'Two'
    metrics = evaluate_recommender(bundle, data)
    assert metrics['recall_at_3'] == 1


@pytest.fixture
def flight_client(tmp_path):
    df = flight_frame()
    model = flight_pipeline(Ridge()).fit(df[FLIGHT_INPUTS], df.price)
    bundle = {'pipeline': model, 'metadata': {'categories': {'from': ['A'], 'to': ['B'], 'flightType': ['economic'], 'agency': ['Agency']},
              'numeric_ranges': {'time': [1, 4], 'distance': [100, 1000]}, 'training_date_max': '2021-12-31'}}
    save_bundle('flights', bundle, {'quality_gate': {'passed': True}}, 'test', tmp_path)
    promote('flights', tmp_path)
    return create_app(tmp_path, tmp_path).test_client()


def valid_request():
    return {'from': 'A', 'to': 'B', 'flightType': 'economic', 'agency': 'Agency', 'time': 2., 'distance': 500., 'date': '2021-03-01'}


def test_api_real_prediction_and_version(flight_client):
    response = flight_client.post('/api/v1/flights/predict', json=valid_request())
    assert response.status_code == 200
    assert response.json['predicted_price'] > 0
    assert response.json['model_version'] == 'test'
    assert response.headers['X-Request-ID'] == response.json['request_id']


@pytest.mark.parametrize('field,value', [('time', -1), ('distance', 'far'), ('distance', True), ('from', 'Unknown'), ('date', '2023-02-30'), ('date', 1)])
def test_api_rejects_invalid_inputs(flight_client, field, value):
    data = valid_request()
    data[field] = value
    assert flight_client.post('/api/v1/flights/predict', json=data).status_code == 400


def test_api_rejects_missing_extra_non_object(flight_client):
    for data in [{}, [], {'unexpected': 2}]:
        assert flight_client.post('/api/v1/flights/predict', json=data).status_code == 400
