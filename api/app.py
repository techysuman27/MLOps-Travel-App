"""Explicit contracts, startup loading, and observable inference."""
import json
import logging
import math
import os
import time
import uuid
from datetime import date
from pathlib import Path

import pandas as pd
from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException

from voyage.artifacts import load_bundle
from voyage.recommendation import recommend


class InputError(ValueError):
    pass


def number(data, key, minimum=0, maximum=1e7, integer=False):
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f'{key} must be a finite number')
    if not minimum <= value <= maximum or (integer and value != int(value)):
        raise InputError(f'{key} must be between {minimum} and {maximum}' + (' and an integer' if integer else ''))
    return int(value) if integer else float(value)


def create_app(model_dir=None, reports_dir=None):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024
    root = Path(model_dir or os.environ.get('MODEL_DIR', 'models'))
    reports = Path(reports_dir or os.environ.get('REPORTS_DIR', 'reports'))
    bundles, manifests, failures = {}, {}, []
    for task in ['flights', 'classification', 'hotels']:
        try:
            bundles[task], manifests[task] = load_bundle(task, root)
        except Exception as exc:
            app.logger.error('Model %s could not load: %s', task, type(exc).__name__)
            failures.append(task)
    app.extensions['voyage_models'] = bundles

    @app.before_request
    def start_request():
        g.request_id = uuid.uuid4().hex
        g.start = time.perf_counter()

    @app.after_request
    def finish_request(response):
        response.headers['X-Request-ID'] = g.request_id
        response.headers['X-Content-Type-Options'] = 'nosniff'
        app.logger.info(json.dumps({'request_id': g.request_id, 'path': request.path,
                                    'status': response.status_code, 'latency_ms': round((time.perf_counter() - g.start) * 1000, 2)}))
        return response

    @app.errorhandler(InputError)
    def bad_input(exc):
        return jsonify(error=str(exc), request_id=g.request_id), 400

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return jsonify(error=exc.description, request_id=g.request_id), exc.code

    @app.errorhandler(Exception)
    def server_error(exc):
        app.logger.exception('Inference error; request_id=%s', g.request_id)
        return jsonify(error='Internal service error', request_id=g.request_id), 500

    def payload(allowed, required):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise InputError('Request must be a JSON object')
        missing, extra = set(required) - data.keys(), data.keys() - set(allowed)
        if missing or extra:
            raise InputError(f'Missing fields: {sorted(missing)}; unknown fields: {sorted(extra)}')
        return data

    def available(task):
        if task not in bundles:
            from flask import abort
            abort(503, description=f'{task} model is unavailable')
        return bundles[task]

    @app.get('/')
    def index():
        return jsonify(service='Voyage Analytics', api_version='v1', endpoints=['/health/live', '/health/ready', '/api/v1/model-info', '/api/v1/flights/predict', '/api/v1/classification/predict', '/api/v1/hotels/recommend'])

    @app.get('/health/live')
    def live():
        return jsonify(status='alive')

    @app.get('/health/ready')
    def ready():
        return jsonify(status='ready' if not failures else 'not_ready', unavailable=failures), (503 if failures else 200)

    @app.get('/api/v1/model-info')
    def model_info():
        return jsonify({k: {'version': v['version'], 'selected': v['report']['selected'],
                            'test_metrics': v['report']['test_metrics'], 'limitations': v['report']['limitations']} for k, v in manifests.items()})

    @app.get('/api/v1/catalogue')
    def catalogue():
        return jsonify(json.loads((reports / 'catalogue.json').read_text(encoding='utf-8')))

    @app.post('/api/v1/flights/predict')
    def flight_predict():
        bundle = available('flights')
        fields = ['from', 'to', 'flightType', 'agency', 'time', 'distance', 'date']
        data = payload(fields, fields)
        for field, choices in bundle['metadata']['categories'].items():
            if not isinstance(data[field], str) or data[field] not in choices:
                raise InputError(f'{field} must be one of {choices}')
        if data['from'] == data['to']:
            raise InputError('Origin and destination must differ')
        data['time'] = number(data, 'time', 0.01, 48)
        data['distance'] = number(data, 'distance', 0.01, 20000)
        try:
            if not isinstance(data['date'], str) or len(data['date']) != 10:
                raise ValueError()
            day = date.fromisoformat(data['date'])
        except (ValueError, TypeError):
            raise InputError('date must be a valid YYYY-MM-DD date')
        warnings = ['Historical estimate in dataset currency units; not a live fare quote.']
        if str(day) > bundle['metadata']['training_date_max']:
            warnings.append('Date is beyond the training period; current market accuracy is unverified.')
        for field, bounds in bundle['metadata']['numeric_ranges'].items():
            if not bounds[0] <= data[field] <= bounds[1]:
                warnings.append(f'{field} is outside the training range.')
        price = float(bundle['pipeline'].predict(pd.DataFrame([data]))[0])
        if not math.isfinite(price) or price <= 0:
            raise RuntimeError('Invalid model output')
        return jsonify(predicted_price=round(price, 2), units='dataset currency units', model_version=manifests['flights']['version'], warnings=warnings, request_id=g.request_id)

    @app.post('/api/v1/classification/predict')
    def classification_predict():
        bundle = available('classification')
        data = payload(['company', 'age'], ['company', 'age'])
        if not isinstance(data['company'], str) or data['company'] not in bundle['metadata']['companies']:
            raise InputError('company is not in the dataset catalogue')
        data['age'] = number(data, 'age', 18, 100, integer=True)
        X = pd.DataFrame([data])
        pipeline = bundle['pipeline']
        return jsonify(predicted_dataset_label=str(pipeline.predict(X)[0]),
                       probabilities=dict(zip(map(str, pipeline.classes_), map(float, pipeline.predict_proba(X)[0]))),
                       model_version=manifests['classification']['version'], request_id=g.request_id,
                       warning='Educational source-label prediction only. none is undocumented. Do not infer a person’s identity or use for decisions.')

    @app.post('/api/v1/hotels/recommend')
    def hotel_recommend():
        bundle = available('hotels')
        data = payload(['user_code', 'destination', 'budget', 'k'], [])
        user = number(data, 'user_code', 0, 1e9, integer=True) if 'user_code' in data else None
        budget = number(data, 'budget', 0.01, 1e7) if 'budget' in data else None
        destination = data.get('destination')
        if destination is not None and (not isinstance(destination, str) or destination not in set(bundle['catalogue'].place)):
            raise InputError('destination is not in the catalogue')
        k = number(data, 'k', 1, 9, integer=True) if 'k' in data else 3
        return jsonify(recommendations=recommend(bundle, user, destination, budget, k),
                       model_version=manifests['hotels']['version'], request_id=g.request_id,
                       note='Nine historical hotels, one per destination. Scores are ranking weights, not ratings or availability.')

    return app


if __name__ == '__main__':
    from waitress import serve
    logging.basicConfig(level=logging.INFO)
    serve(create_app(), host='127.0.0.1', port=int(os.environ.get('PORT', '8000')))
