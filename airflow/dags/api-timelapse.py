from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)

def publish_message_to_redis(channel, message):
    redis_client.publish(channel, message)

def push_to_redis(result, key):
    try:
        serialized_data = json.dumps(result)
        redis_client.set(key, serialized_data)
    except Exception as e:
        raise

def call_python_timelapse(region: str, **kwargs):
    url = f"http://python-timelapse:5000/generate_video?region={region}"
    response = requests.get(url)
    if response.status_code == 200:
        publish_message_to_redis('dag_notifications', 'timelapse')
    else:
        publish_message_to_redis('dag_notifications', 'dag_failed')
        raise Exception(f"Failed to fetch filtered links for tiem {region}. Status code: {response.status_code}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.today(),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def create_video(**context):
    region = context['dag_run'].conf.get('region', 'europe')  # Par défaut '2021' si aucune année n'est fournie
    call_python_timelapse(region, **context)

dag = DAG(
    'python-timelapse-workflow',
    default_args=default_args,
    description='DAG pour récupérer un timelapse',
    schedule_interval=None,
)

t1 = PythonOperator(
    task_id='create_video',
    python_callable=create_video,
    provide_context=True,
    dag=dag,
)