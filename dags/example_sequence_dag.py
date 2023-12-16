
from datetime import datetime, timedelta
from textwrap import dedent
import pendulum
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

def random_branch_path():
    from random import randint
    return "path1" if randint(1, 2) == 1 else "my_name_en"

with DAG( 
    dag_id="tutorial-dag-sequence",
    description='tutorial DAG sequence',
    schedule_interval=timedelta(seconds=50),
    start_date=pendulum.datetime(2023, 12, 15,tz='Asia/Seoul'),
    dagrun_timeout=timedelta(seconds=50),
    catchup=False,
    tags=['dufwn'] 
) as dag:
    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    t2 = BranchPythonOperator(
        task_id='branch',
        python_callable=random_branch_path,
    )
    
    t3 = BashOperator(
        task_id='my_name_ko',
        depends_on_past=False,
        bash_command='echo "안녕하세요."',
    )

    t4 = BashOperator(
        task_id='my_name_en',
        depends_on_past=False,
        bash_command='echo "Hi"',
    )

    complete = BashOperator(
        task_id='complete',
        depends_on_past=False,
        bash_command='echo "complete~!"',
        trigger_rule=TriggerRule.NONE_FAILED
    )

    dummy_1 = DummyOperator(task_id="path1")


    t1 >> t2 >> dummy_1 >> t3 >> complete
    t1 >> t2 >> t4 >> complete
