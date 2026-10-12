"""Operate only the password-protected local capstone Jenkins demo."""
import argparse
import json
import sys
from pathlib import Path
import requests
sys.stdout.reconfigure(encoding='utf-8')

parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['status', 'build', 'log'])
parser.add_argument('--local-deploy', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
session = requests.Session()
session.auth = ('voyage-admin', (root / 'artifacts-local/jenkins-admin-password').read_text().strip())
base = 'http://127.0.0.1:8081'
job = base + '/job/Voyage-Travel-CI'
if args.action == 'build':
    crumb = session.get(base + '/crumbIssuer/api/json', timeout=30)
    crumb.raise_for_status()
    data = crumb.json()
    settings = session.get(job + '/api/json', timeout=30)
    settings.raise_for_status()
    parameterized = any(p.get('_class', '').endswith('ParametersDefinitionProperty') for p in settings.json().get('property', []))
    endpoint = '/buildWithParameters' if parameterized else '/build'
    result = session.post(job + endpoint, headers={data['crumbRequestField']: data['crumb']},
                          data={'LOCAL_DEPLOY': str(args.local_deploy).lower(), 'PUBLISH': 'false', 'DEPLOY': 'false', 'IMAGE_REPOSITORY': 'ghcr.io/techysuman27/voyage-api'}, timeout=30)
    result.raise_for_status()
    print(f'Project pipeline queued; local deployment={args.local_deploy}, registry and Kubernetes deployment disabled.')
elif args.action == 'status':
    result = session.get(job + '/lastBuild/api/json', timeout=30)
    result.raise_for_status()
    data = result.json()
    print(json.dumps({k: data.get(k) for k in ['number', 'building', 'result', 'duration', 'url']}, indent=2))
else:
    result = session.get(job + '/lastBuild/consoleText', timeout=30)
    result.raise_for_status()
    # This demo never passes registry tokens or cluster credentials to a build.
    path = root / 'docs/evidence/jenkins-console.txt'
    path.write_text(result.text, encoding='utf-8')
    print('\n'.join(result.text.splitlines()[-35:]))
