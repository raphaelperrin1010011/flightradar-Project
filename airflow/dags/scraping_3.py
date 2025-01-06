from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import requests
import json
import logging

def call_process_csv(link_1: str, link_2_list: list, **kwargs):
    # Utilisation du logger d'Airflow
    logger = logging.getLogger("airflow.task")
    url = f"http://python-data:8100/process_csv/{link_1}"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'link_2': link_2_list})
    logger.info(f"URL: {url}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Data: {data}")
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        logger.info(f"CSV traité avec succès pour {link_1} et {link_2_list}.")
    else:
        logger.error(f"Échec du traitement CSV pour {link_1} et {link_2_list}. Code de statut: {response.status_code}")
        raise Exception(f"Failed to process CSV for link_1 {link_1} and link_2 {link_2_list}. Status code: {response.status_code}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.today(),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def task_call_process_csv(**context):
    logger = logging.getLogger("airflow.task")
    logger.info("Démarrage de la tâche 'process_csv'")
    link_1 = context['dag_run'].conf.get('link_1')
    link_2_list = context['dag_run'].conf.get('link_2')
    if not link_1 or not link_2_list:
        logger.error("Les paramètres 'link_1' et 'link_2' sont requis.")
        raise ValueError("Les paramètres 'link_1' et 'link_2' sont requis.")
    logger.info(f"Paramètres reçus - link_1: {link_1}, link_2: {link_2_list}")
    call_process_csv(link_1, link_2_list, **context)

dag = DAG(
    'process_csv_workflow',
    default_args=default_args,
    description='DAG pour traiter les fichiers CSV',
    schedule_interval=None,
)

t1 = PythonOperator(
    task_id='process_csv',
    python_callable=task_call_process_csv,
    provide_context=True,
    dag=dag,
)