import argparse
import time
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
args = parser.parse_args()
for _ in range(30):
    try:
        if requests.get(args.url.rstrip('/') + '/health/ready', timeout=3).status_code == 200:
            break
    except requests.RequestException:
        pass
    time.sleep(2)
else:
    raise SystemExit('Readiness timed out')
