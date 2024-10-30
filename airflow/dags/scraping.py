from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
import json

# Définir les paramètres par défaut du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 24),  # Date de départ
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définir le DAG
dag = DAG(
    'scraping_workflow',
    default_args=default_args,
    description='DAG pour gérer le workflow utilisateur avec des appels API',
    schedule_interval=None,
)

# Fonction pour appeler l'API de filtrage des liens d'année
def call_filtered_links(year: str):
    url = f"http://python-data:8100/filtered_links/{year}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['filtered_links']
    else:
        raise Exception(f"Failed to fetch filtered links for year {year}. Status code: {response.status_code}")

# Fonction pour appeler l'API de filtrage des sous-liens
def call_filtered_links_2(link_1: str):
    url = f"http://python-data:8100/filtered_links_2/{link_1}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['filtered_links_2']
    else:
        raise Exception(f"Failed to fetch filtered links 2 for link_1 {link_1}. Status code: {response.status_code}")

# Fonction pour appeler l'API de traitement CSV
def call_process_csv(link_1: str, link_2_list: list):
    url = f"http://python-data:8100/process_csv/{link_1}"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'link_2': link_2_list})
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("CSV processed successfully.")
    else:
        raise Exception(f"Failed to process CSV for link_1 {link_1} and link_2 {link_2_list}. Status code: {response.status_code}")

# Définir les tâches dans le DAG

# Tâche 1 : Sélection de l'année et récupération des liens filtrés
def task_select_year(**context):
    year = context['dag_run'].conf.get('year', '2021')  # Par défaut '2021' si aucune année n'est fournie
    return call_filtered_links(year)

t1 = PythonOperator(
    task_id='select_year',
    python_callable=task_select_year,
    provide_context=True,
    dag=dag,
)

# Tâche 2 : Sélection du lien principal (link_1) et récupération des sous-liens (link_2)
def task_select_link_1(**context):
    link_1 = context['dag_run'].conf.get('link_1', None)
    if not link_1:
        raise Exception("link_1 is required to proceed.")
    return call_filtered_links_2(link_1)

t2 = PythonOperator(
    task_id='select_link_1',
    python_callable=task_select_link_1,
    provide_context=True,
    dag=dag,
)

# Tâche 3 : Traitement du CSV après sélection des sous-liens
def task_process_csv(**context):
    link_1 = context['dag_run'].conf.get('link_1', None)
    link_2 = context['task_instance'].xcom_pull(task_ids='select_link_1')
    if not link_1 or not link_2:
        raise Exception("Both link_1 and link_2 are required to process CSV.")
    call_process_csv(link_1, link_2)

t3 = PythonOperator(
    task_id='process_csv',
    python_callable=task_process_csv,
    provide_context=True,
    dag=dag,
)

# Dépendances entre les tâches
t1 >> t2 >> t3
