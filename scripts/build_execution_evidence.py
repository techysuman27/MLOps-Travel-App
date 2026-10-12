"""Render captured command outputs as a readable evidence sheet, not a live dashboard."""
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
evidence = root / 'docs/evidence'
sections = []
for title, path in [
    ('Docker API container status', evidence / 'docker-status.txt'),
    ('Kubernetes rollout and manual scaling', evidence / 'kubernetes-rollout.txt'),
    ('Bounded inference test: 200 requests, eight workers', root / 'reports/load_test.json'),
    ('Public Flask prediction response', evidence / 'public-api-response.json'),
]:
    if path.exists():
        contents = path.read_text(encoding='utf-8-sig')
        if path.suffix == '.json':
            contents = json.dumps(json.loads(contents), indent=2)
        sections.append(f'<section><h2>{escape(title)}</h2><pre>{escape(contents)}</pre></section>')
html = '''<!doctype html><html lang="en"><meta charset="utf-8"><title>Voyage execution evidence</title>
<style>body{max-width:1160px;margin:36px auto;padding:0 24px;font:16px Arial;color:#163349;background:#f5f7fa}
h1{font-size:30px}h2{font-size:19px}section{background:white;border:1px solid #dbe5eb;border-radius:12px;padding:16px 22px;margin:18px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.6 Consolas,monospace}p{line-height:1.6}</style>
<h1>Voyage Analytics — execution evidence</h1>
<p>Captured output from actual verification commands on 11 October 2026. This sheet displays saved results; it is not a live service dashboard.</p>
<p>Kubernetes was manually scaled from two to three replicas. The load test used a port-forward to one selected pod; it does not establish traffic balancing, automatic scaling or production capacity.</p>'''
html += ''.join(sections)
html += f'<p>Report generated: {datetime.now(timezone.utc).isoformat()}</p></html>'
(evidence / 'execution-report.html').write_text(html, encoding='utf-8')
