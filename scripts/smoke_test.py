"""Fail a deployment if the actual prediction path is not usable."""
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000')
args = parser.parse_args()
root = args.url.rstrip('/')
ready = requests.get(root + '/health/ready', timeout=20)
ready.raise_for_status()
request = {'from': 'Recife (PE)', 'to': 'Florianopolis (SC)', 'flightType': 'firstClass',
           'agency': 'FlyingDrops', 'time': 1.76, 'distance': 676.53, 'date': '2023-06-15'}
response = requests.post(root + '/api/v1/flights/predict', json=request, timeout=30)
response.raise_for_status()
assert response.json()['predicted_price'] > 0
assert response.json()['model_version']
bad = requests.post(root + '/api/v1/flights/predict', json={}, timeout=10)
assert bad.status_code == 400
hotel = requests.post(root + '/api/v1/hotels/recommend', json={'k': 3}, timeout=10)
hotel.raise_for_status()
assert len(hotel.json()['recommendations']) == 3
print('Readiness, prediction, validation and recommendation checks passed.')
