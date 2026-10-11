"""Execute submitted notebooks and retain real outputs; fail on any cell error."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

for path in sorted(Path('notebooks').glob('*.ipynb')):
    print('Executing', path, flush=True)
    notebook = nbformat.read(path, as_version=4)
    NotebookClient(notebook, timeout=600, kernel_name='python3', resources={'metadata': {'path': str(Path.cwd())}}).execute()
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    print('Verified', path, flush=True)
