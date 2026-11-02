from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import random
import statistics

default_args = {
    'owner': 'Sai Dheekshit Reddy Antham',
    'start_date': datetime(2024, 6, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'cloud_composer_tutorial',
    default_args=default_args,
    description='Introductory DAG for Cloud Composer',
    schedule=None,  # For manual triggering
    catchup=False,
    tags=['lab1', 'tutorial'],
) as dag:

    # Task 1: Hello World (BashOperator), uses a Jinja template for the run date
    hello_world_task = BashOperator(
        task_id='hello_world',
        bash_command='echo "Hello, Cloud Composer! Run date: {{ ds }}"',
    )

    # Task 2: Simple Python Task (PythonOperator)
    def say_hello():
        print("This is a simple Python task in Airflow.")

    say_hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=say_hello,
    )

    # Task 3: Generate some numbers; the return value is pushed to XCom
    def generate_numbers():
        numbers = [random.randint(1, 100) for _ in range(10)]
        print(f"Generated numbers: {numbers}")
        return numbers

    generate_numbers_task = PythonOperator(
        task_id='generate_numbers',
        python_callable=generate_numbers,
    )

    # Task 4: Pull the numbers from XCom and compute summary stats
    def compute_stats(ti):
        numbers = ti.xcom_pull(task_ids='generate_numbers')
        stats = {
            'count': len(numbers),
            'min': min(numbers),
            'max': max(numbers),
            'mean': round(statistics.mean(numbers), 2),
        }
        print(f"Stats: {stats}")
        return stats

    compute_stats_task = PythonOperator(
        task_id='compute_stats',
        python_callable=compute_stats,
    )

    # Task 5: Read the stats back from XCom inside a Bash command
    goodbye_task = BashOperator(
        task_id='goodbye',
        bash_command='echo "Mean was {{ ti.xcom_pull(task_ids=\'compute_stats\')[\'mean\'] }}. Goodbye!"',
    )

    # Task Dependencies: say_hello and generate_numbers run in parallel after hello_world
    hello_world_task >> [say_hello_task, generate_numbers_task]
    generate_numbers_task >> compute_stats_task
    [say_hello_task, compute_stats_task] >> goodbye_task
