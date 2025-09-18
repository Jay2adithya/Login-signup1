from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import requests
import sys

sys.path.append('/opt/airflow')
from loading_path2 import loading_path
from metrics import get_metrics
def fetching_path(ti, **kwargs):
    path, doc_id = loading_path()
    if not path or not doc_id:
        return 'skip'
    ti.xcom_push(key='path', value=path)
    ti.xcom_push(key='doc_id', value=doc_id)
    return 't2'
def runmetrics(ti, **kwargs):
    path = ti.xcom_pull(task_ids='t1', key='path')
    metrics = get_metrics(path)
    ti.xcom_push(key='metrics', value=metrics)
    return metrics
def loadmetrics(ti, **kwargs):
    doc_id = ti.xcom_pull(task_ids='t1', key='doc_id')
    metrics = ti.xcom_pull(task_ids='t2', key='metrics')
    url = "http://backend:5000/metrics"
    payload = {
        "metrics": metrics,
        "status": 1,
        "doc_id": doc_id
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        print("Metrics stored successfully in Flask app")
    else:
        raise Exception(f"Failed to store metrics: {response.status_code} - {response.text}")
with DAG("thirdflow",
         start_date=datetime(2025, 8, 14),
         schedule_interval=None,
         catchup=False) as dag:
    fetch_path = BranchPythonOperator(
        task_id='t1',
        python_callable=fetching_path
    )
    calculatemetrics = PythonOperator(
        task_id='t2',
        python_callable=runmetrics
    )
    load_result = PythonOperator(
        task_id='t3',
        python_callable=loadmetrics
    )
    skip = EmptyOperator(task_id='skip')
    end = EmptyOperator(task_id='end')
    fetch_path >> [calculatemetrics, skip]
    calculatemetrics >> load_result >> end
    skip >> end
