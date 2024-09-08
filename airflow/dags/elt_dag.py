from datetime import datetime
from airflow import DAG
from docker.types import Mount

from airflow.operators.python import PythonOperator

from airflow.providers.docker.operators.docker import DockerOperator
import subprocess



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry':False
}

def run_elt_script():
    script_path = "/opt/airflow/elt_script/elt_script.py"
    result = subprocess.run(
        ["python", script_path], capture_output=True, text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Script failed with error: {result.stderr}")
    else:
        print(result.stdout)


with DAG(
    dag_id= 'elt_using_dbt',
    description= 'An ELT workflow with dbt',
    default_args= default_args,
    start_date= datetime(2024, 9, 8),
    catchup= False,
    schedule_interval= '@daily'
) as dag:
    
    t1 = PythonOperator(
        task_id='run_elt_script',
        python_callable=run_elt_script,
        dag=dag
        
    ),
    
    t2 = DockerOperator(
        task_id='dbt_run',
        image='ghcr.io/dbt-labs/dbt-postgres:1.8.2',
        container_name='dbt',
        environment={
            'DBT_PROFILE': 'dbt_project'  # This should match the profile name in profiles.yml
        },
        command=[
            'run',
            '--profiles-dir', '/root',
            '--project-dir', '/opt/dbt',
            '--full-refresh'
        ],
        auto_remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge',
        mounts=[
            Mount(source='/home/centos/ELT-project-dbt/dbt_project', target='/opt/dbt', type='bind'),
            Mount(source='/home/centos/.dbt', target='/root', type='bind')
        ],
        mount_tmp_dir=False,  # Disable temp directory mounting
        extra_hosts={
            'host.docker.internal': 'host-gateway'  # Add this to resolve host name
        },
        dag=dag
    )


t1 >> t2