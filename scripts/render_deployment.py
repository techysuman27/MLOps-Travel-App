import os
from pathlib import Path
import yaml

image = os.environ['RELEASE_IMAGE']
if '@sha256:' not in image:
    raise ValueError('Deployment requires an immutable image digest')
documents = list(yaml.safe_load_all(Path('kubernetes/deployment.yml').read_text()))
for document in documents:
    if document['kind'] == 'Deployment':
        document['spec']['template']['spec']['containers'][0]['image'] = image
Path('reports').mkdir(exist_ok=True)
Path('reports/release-deployment.yml').write_text(yaml.safe_dump_all(documents))
