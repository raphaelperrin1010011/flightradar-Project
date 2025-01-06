from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import logging
import redis

logger = logging.getLogger("airflow.task")
redis_client = redis.Redis(host='redis', port=6379, db=0)

def publish_message_to_redis(channel, message):
    redis_client.publish(channel, message)

def push_to_redis(result, key):
    try:
        serialized_data = json.dumps(result)
        redis_client.set(key, serialized_data)
        logger.info(f"Résultat stocké dans Redis sous la clé '{key}'.")
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture dans Redis : {str(e)}")
        raise

def call_filtered_links_2(link_1: str, **kwargs):
    url = f"http://python-data:8100/filtered_links_2/{link_1}"
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f"Requête réussie pour les sous-liens de {link_1}.")
        result = response.json()['filtered_links_2']
        push_to_redis(result, "filtered_links_2")
        publish_message_to_redis('dag_notifications', 'filtered_links_2')
    else:
        logger.error(f"Échec de la requête pour les sous-liens de {link_1}. Code de statut: {response.status_code}")
        publish_message_to_redis('dag_notifications', 'dag_failed')
        raise Exception(f"Failed to fetch filtered links 2 for link_1 {link_1}. Status code: {response.status_code}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.today(),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def task_select_link(**context):
    date = context['dag_run'].conf.get('date', '2021')  # Par défaut '2021' si aucune année n'est fournie
    call_filtered_links_2(date, **context)

dag = DAG(
    'filtered_links_2_workflow',
    default_args=default_args,
    description='DAG pour récupérer les sous-liens',
    schedule_interval=None,
)

t1 = PythonOperator(
    task_id='select_link_1',
    python_callable=task_select_link,
    provide_context=True,
    dag=dag,
)