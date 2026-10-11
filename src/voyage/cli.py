"""CLI shared by local development, Colab, Airflow and CI."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['validate', 'train', 'promote', 'metadata'])
    parser.add_argument('--task', choices=['flights', 'classification', 'hotels', 'all'], default='all')
    parser.add_argument('--data-dir', default='data/raw')
    parser.add_argument('--model-dir', default='models')
    parser.add_argument('--reports-dir', default='reports')
    args = parser.parse_args()
    from voyage.data import load_data, sha256
    from voyage.artifacts import write_json, promote
    tasks = ['flights', 'classification', 'hotels'] if args.task == 'all' else [args.task]
    if args.command in ['validate', 'metadata']:
        frames = load_data(args.data_dir)
        audit = {k: {'rows': len(v), 'sha256': sha256(Path(args.data_dir) / f'{k}.csv')} for k, v in frames.items()}
        write_json(Path(args.reports_dir) / 'source_validation.json', audit)
        if args.command == 'metadata':
            flights, hotels, users = (frames[k] for k in ['flights', 'hotels', 'users'])
            metadata = {'counts': {k: len(v) for k, v in frames.items()},
                        'cities': sorted(flights['from'].unique().tolist()),
                        'flight_types': sorted(flights.flightType.unique().tolist()),
                        'agencies': sorted(flights.agency.unique().tolist()),
                        'companies': sorted(users.company.unique().tolist()),
                        'hotel_catalogue': hotels.groupby(['name', 'place']).agg(nightly_price=('price', 'median'), bookings=('name', 'size')).reset_index().to_dict('records'),
                        'gender_counts': users.gender.value_counts().to_dict()}
            write_json(Path(args.reports_dir) / 'catalogue.json', metadata)
        print(json.dumps(audit, indent=2))
    elif args.command == 'train':
        from voyage.training import run_training
        for task in tasks:
            run_training(task, args.data_dir, args.model_dir, args.reports_dir)
    else:
        for task in tasks:
            print(promote(task, args.model_dir)['version'])


if __name__ == '__main__':
    main()
