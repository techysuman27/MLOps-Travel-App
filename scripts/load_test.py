"""Bounded load for a local scaling demo; no unbounded traffic generation."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import time
import requests
from voyage.artifacts import write_json

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:18080')
parser.add_argument('--requests', type=int, default=200)
parser.add_argument('--workers', type=int, default=8)
args = parser.parse_args()
if not 1 <= args.requests <= 2000 or not 1 <= args.workers <= 16:
    parser.error('Use 1–2000 requests and 1–16 workers')
payload = {'from': 'Recife (PE)', 'to': 'Florianopolis (SC)', 'flightType': 'firstClass', 'agency': 'FlyingDrops', 'time': 1.76, 'distance': 676.53, 'date': '2023-06-15'}

def call(_):
    start = time.perf_counter()
    try:
        r = requests.post(args.url.rstrip('/') + '/api/v1/flights/predict', json=payload, timeout=30)
        okay = r.status_code == 200 and r.json().get('predicted_price', 0) > 0
    except (requests.RequestException, ValueError):
        okay = False
    return (time.perf_counter() - start) * 1000, okay

with ThreadPoolExecutor(max_workers=args.workers) as executor:
    results = list(executor.map(call, range(args.requests)))
latency = sorted(x[0] for x in results)
report = {'requests': len(results), 'workers': args.workers, 'successful': sum(x[1] for x in results),
          'p50_ms': latency[len(latency)//2], 'p95_ms': latency[min(len(latency)-1, int(len(latency)*.95))]}
write_json('reports/load_test.json', report)
print(report)
if report['successful'] != args.requests:
    raise SystemExit('Some prediction requests failed')
