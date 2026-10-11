"""Download only the three course CSVs; verify the archive when configured."""
import argparse
import hashlib
from pathlib import Path
import urllib.request
import zipfile

URL = 'https://drive.google.com/uc?export=download&id=1fd21ljY3KS3B6ZPITmSlDHVD2yff46OC'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='data/raw')
    args = parser.parse_args()
    destination = Path(args.output)
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination.parent / 'travel_capstone.zip'
    if not archive.exists():
        urllib.request.urlretrieve(URL, archive)
    with zipfile.ZipFile(archive) as z:
        for name in ['flights.csv', 'users.csv', 'hotels.csv']:
            content = z.read(name)
            (destination / name).write_bytes(content)
            print(name, hashlib.sha256(content).hexdigest())


if __name__ == '__main__':
    main()
