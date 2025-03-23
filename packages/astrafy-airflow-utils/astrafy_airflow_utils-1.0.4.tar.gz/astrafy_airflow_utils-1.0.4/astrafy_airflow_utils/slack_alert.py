from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.hooks.base_hook import BaseHook
from airflow.configuration import conf


SLACK_CONN_ID = "slack_airflow"


def task_fail_slack_alert(context):
    webserver_url = conf.get('webserver', 'base_url')
    dag_id = context.get("task_instance").dag_id
    task_id = context.get("task_instance").task_id
    run_id = context.get("task_instance").run_id
    execution_date = context.get("execution_date")
    dag_url = f"{webserver_url}/dags/{dag_id}/grid?execution_date={execution_date.isoformat()}&tab=graph&dag_run_id={run_id}"

    slack_msg = """
            :red_circle: Task Failed.
            *Task*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}
            *Dag URL*: <{url}|View in Airflow>
            """.format(
        task=task_id,
        dag=dag_id,
        exec_date=execution_date,
        url=dag_url
    )
    failed_alert = SlackWebhookOperator(
        task_id="slack_fail_alert", 
        slack_webhook_conn_id=SLACK_CONN_ID,
        message=slack_msg,
    )
    return failed_alert.execute(context=context)
