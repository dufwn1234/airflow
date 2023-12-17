
from datetime import datetime, timedelta
import pendulum
from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule


import sys, os
sys.path.append(os.getcwd())

from MLproject.titanic import *
from utils.slack_alert import SlackAlert

titanic = TitanicMain()
slack = SlackAlert("#airflow", "xoxb-6362974347713-6357670735395-ffEQMmEQ6x7oz5tSoddEb9qz")

def print_result(**kwargs):
    r = kwargs["task_instance"].xcom_pull(key='result_msg')
    print("message : ", r)

with DAG( 
    dag_id="tutorial-slack-ml-op",
    description='tutorial DAG ml with slack',
    schedule_interval=timedelta(minutes=50),
    start_date=datetime(2022, 2, 1),
    tags=['dufwn'],
    catchup=False,
    on_success_callback=slack.success_msg,
    on_failure_callback=slack.fail_msg 
) as dag:
    start = BashOperator(
        task_id='start',
        bash_command='echo "start!"',
    )

    prepro_task = PythonOperator(
        task_id='preprocessing',
        python_callable=titanic.prepro_data,
        op_kwargs={'f_name': "train"}
    )
    
    modeling_task = PythonOperator(
        task_id='modeling',
        python_callable=titanic.run_modeling,
        op_kwargs={'n_estimator': 100, 'flag' : True}
    )

    msg = PythonOperator(
        task_id='msg',
        python_callable=print_result
    )

    complete = BashOperator(
        task_id='complete_bash',
        bash_command='echo "complete~!"',
    )

    start >> prepro_task >> modeling_task >> msg >> complete
