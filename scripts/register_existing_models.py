"""Register already-logged, verified pipelines without rerunning model selection."""
import json
from pathlib import Path
import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri('sqlite:///mlflow.db')
client = MlflowClient()
for task in ['flights', 'classification']:
    manifest = json.loads(Path(f'models/{task}.json').read_text())
    name = f'voyage-{task}'
    versions = client.search_model_versions(f"name='{name}'")
    same = [v for v in versions if v.run_id == manifest['version']]
    if same:
        version = same[0]
    else:
        version = mlflow.register_model(f"runs:/{manifest['version']}/pipeline", name)
    print(task, 'registered version', version.version, 'run', manifest['version'])
