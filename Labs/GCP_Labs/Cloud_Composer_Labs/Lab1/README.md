# Watch the tutorial video for this lab at [Cloud Composer Lab1](https://youtu.be/JB_I416LQ7A)


# Google Cloud Composer Airflow Tutorial

Welcome to the Google Cloud Composer Airflow tutorial! This guide will help you understand the basics of using Apache Airflow with Google Cloud Composer, set up a simple Directed Acyclic Graph (DAG), and deploy it on Google Cloud Composer.

## What is Google Cloud Composer?

Google Cloud Composer is a fully managed workflow orchestration service built on Apache Airflow. It allows you to author, schedule, and monitor workflows as directed acyclic graphs (DAGs) of tasks. Cloud Composer helps you automate and orchestrate tasks across cloud and on-premises environments.

## What is Apache Airflow?

Apache Airflow is an open-source platform to programmatically author, schedule, and monitor workflows. It allows you to define workflows as code, ensuring they are versionable, testable, and maintainable. Airflow uses DAGs to represent workflows, where each node is a task and edges define the execution order.

## Tutorial Overview

In this tutorial, we will create a simple DAG consisting of two tasks:
1. A `BashOperator` task that prints "Hello, Cloud Composer!".
2. A `PythonOperator` task that runs a simple Python function.

Refer to [this page](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html) for more operators.


### Prerequisites

- A Google Cloud Platform account.
- A Google Cloud Composer environment set up.
- Basic knowledge of Python and Airflow concepts.

## Explanation of the DAG
- default_args: Contains default arguments for the DAG. Here, it specifies the owner, start date, and retry settings.
- dag: Defines the DAG with an ID, default arguments, description, and schedule.
- hello_world_task: A BashOperator that prints "Hello, Cloud Composer!" along with the run date.
- say_hello_task: A PythonOperator that runs a simple Python function.
- generate_numbers_task: A PythonOperator that makes 10 random numbers and pushes them to XCom.
- compute_stats_task: A PythonOperator that pulls the numbers from XCom and computes count, min, max, and mean.
- goodbye_task: A BashOperator that reads the mean from XCom using a Jinja template and prints it.

## My Changes

- Switched to the current Airflow 2 imports (`airflow.operators.python` / `airflow.operators.bash`) instead of the deprecated `python_operator` / `bash_operator` modules.
- Replaced the deprecated `schedule_interval` with `schedule`, added `catchup=False` and tags, and defined the DAG with a `with DAG(...)` block.
- Added `retries` and `retry_delay` to `default_args`.
- Used a Jinja template (`{{ ds }}`) in the `hello_world` task to print the run date.
- Added three tasks that pass data between each other with XCom: `generate_numbers` → `compute_stats` → `goodbye`.
- Changed the task graph so `say_hello` and `generate_numbers` run in parallel after `hello_world`, and both must finish before `goodbye`.
- Tested the DAG locally with `airflow dags test` (Airflow 2.9.1); all tasks succeeded.

```
hello_world ──┬──> say_hello ──────────────────────────────┬──> goodbye
              └──> generate_numbers ──> compute_stats ─────┘
```

## Setting Up the Environment

1. **Create a Google Cloud Composer environment:**
   - Navigate to the Cloud Console.
   - Go to the Cloud Composer section.
   - Create a new environment.

2. **Upload the DAG to Cloud Composer:**
   - Once the environment is ready, upload the DAG file to the `dags` folder in your Cloud Storage bucket associated with the Composer environment.

3. **Trigger the DAG:**
   - Go to the Airflow web interface through the Cloud Composer environment.
   - Manually trigger the DAG and observe the task execution.


## Conclusion
This tutorial provided a basic introduction to creating and deploying a DAG in Google Cloud Composer using Apache Airflow. With these foundations, you can start building more complex workflows to automate various tasks in your cloud and on-premises environments.


## Important Links

- Quickstart Guide to Google Cloud Composer - [Getting Started With Composer](https://cloud.google.com/composer/docs/run-apache-airflow-dag)
- Installing Google Cloud CLI -  [Installing gcloud](https://cloud.google.com/sdk/docs/install-sdk)
- Identity Management of Cloud Composer - [Control Access](https://cloud.google.com/composer/docs/how-to/access-control#composer-sa)
- Airflow Operators - [Operators](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html)