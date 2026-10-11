"""Versioned, checksum-verified local bundles; only load our trusted artifacts."""
import json
import os
from pathlib import Path
import joblib
from voyage.data import sha256


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, default=str, allow_nan=False), encoding='utf-8')
    os.replace(temporary, path)


def save_bundle(task, bundle, report, run_id, model_dir='models'):
    root = Path(model_dir)
    directory = root / 'releases' / task / run_id
    directory.mkdir(parents=True, exist_ok=False)
    path = directory / 'model.joblib'
    joblib.dump(bundle, path, compress=3)
    manifest = {'task': task, 'version': run_id, 'artifact': path.relative_to(root).as_posix(),
                'sha256': sha256(path), 'report': report}
    write_json(directory / 'manifest.json', manifest)
    # A candidate is saved first. Promotion is a separate, explicit operation.
    write_json(root / f'{task}.candidate.json', manifest)
    return manifest


def promote(task, model_dir='models'):
    root = Path(model_dir)
    manifest = json.loads((root / f'{task}.candidate.json').read_text(encoding='utf-8'))
    if not manifest['report']['quality_gate']['passed']:
        raise ValueError('Candidate failed the quality gate; existing release preserved')
    if sha256(root / manifest['artifact']) != manifest['sha256']:
        raise ValueError('Candidate checksum mismatch')
    write_json(root / f'{task}.json', manifest)
    return manifest


def load_bundle(task, model_dir='models'):
    root = Path(model_dir).resolve()
    manifest = json.loads((root / f'{task}.json').read_text(encoding='utf-8'))
    path = (root / manifest['artifact']).resolve()
    if not path.is_relative_to(root) or sha256(path) != manifest['sha256']:
        raise ValueError(f'{task}: artifact integrity failure')
    return joblib.load(path), manifest
