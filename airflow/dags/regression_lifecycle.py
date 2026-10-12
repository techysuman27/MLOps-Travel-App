"""Parse-safe DAG: work happens inside tasks, never while importing this file."""
from datetime import datetime, timedelta, timezone
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PYTHON = '/opt/voyage-venv/bin/python'
ROOT = '/opt/project'
RUN_MODELS = ROOT + '/models/candidates/{{ ts_nodash }}'
RUN_REPORTS = ROOT + '/reports/scheduled/{{ ts_nodash }}'
COMMON = f'--data-dir {ROOT}/data/raw --model-dir {RUN_MODELS} --reports-dir {RUN_REPORTS}'

with DAG('voyage_regression_lifecycle', start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
         schedule='0 2 * * 0', catchup=False, max_active_runs=1,
         default_args={'owner': 'techysuman27', 'retries': 1, 'retry_delay': timedelta(minutes=2)},
         tags=['voyage', 'regression']) as dag:
    validate = BashOperator(task_id='validate_source', cwd=ROOT, bash_command=f'{PYTHON} -m voyage.cli validate {COMMON}')
    train = BashOperator(task_id='train_compare_and_evaluate', cwd=ROOT, bash_command=f'{PYTHON} -m voyage.cli train --task flights {COMMON}',
                         env={'OMP_NUM_THREADS': '2', 'OPENBLAS_NUM_THREADS': '2'}, append_env=True)
    approve = BashOperator(task_id='gate_and_approve_candidate', cwd=ROOT, bash_command=f'{PYTHON} -m voyage.cli promote --task flights {COMMON}')
    validate >> train >> approve

# Approved candidates stay under their run folder. A reviewed Jenkins release
# consumes that candidate; scheduling never overwrites the deployed model.
