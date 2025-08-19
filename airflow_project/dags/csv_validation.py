from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import storage
import io
from sqlalchemy import create_engine
import json

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def process_csv(bucket_name, blob_name, user_id, file_id):
   
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    data = blob.download_as_bytes()
    df = pd.read_csv(io.BytesIO(data))

    row_count = len(df)
    null_counts = df.isnull().sum().to_dict()

    engine = create_engine("postgresql+psycopg2://postgres:Jay%4025@postgres:5432/postgres")
    with engine.begin() as conn:
        conn.execute(
            """
            INSERT INTO data_quality_results 
            (user_id, file_id, row_count, null_counts, created_at) 
            VALUES (%s, %s, %s, %s, now())
            """,
            (user_id, file_id, row_count, json.dumps(null_counts))
        )

def run_pipeline(**context):
    conf = context['dag_run'].conf
    process_csv(conf['bucket'], conf['key'], conf['user_id'], conf['file_id'])

with DAG('csv_validation_dag',
         default_args=default_args,
         schedule_interval=None,
         catchup=False,
         description='Validate CSV files uploaded to GCS') as dag:

    run = PythonOperator(
        task_id='run_csv_validation',
        python_callable=run_pipeline,
        provide_context=True
    )
