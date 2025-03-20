import typing as t
from functools import cached_property

from airflow import DAG
from airflow.exceptions import AirflowFailException, AirflowNotFoundException, AirflowSkipException
from airflow.models import BaseOperator
from airflow.models.connection import Connection
from airflow.models.taskinstance import TaskInstance
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.utils.trigger_rule import TriggerRule
from sqlglot import exp

from tobikodata.http_client import V1ApiClient
from tobikodata.http_client.api_models.v1.common import V1Status
from tobikodata.http_client.api_models.v1.dags import V1DagNode
from tobikodata.scheduler_facades.common import (
    poll_next_remote_run,
    poll_until_remote_task_complete,
)


def _wait_until_next_remote_run(ti: TaskInstance, conn_id: str, environment: str) -> bool:
    """
    Intended to be called by a PythonSensor in order to block until a remote run is available to report on
    """
    import logging

    logger = logging.getLogger(__name__)

    # Note that `include_prior_dates` seems to just return a single value from the last run and not an array of values from every historical run
    # This approach allows us to avoid reporting on the same run over and over while still being able to report on runs that start and finish
    # before we even get a chance to poll (and thus wouldnt show if we were only looking for in-progress runs)
    last_airflow_run_id = ti.xcom_pull(key="run_id", include_prior_dates=True)
    logger.info(f"Last run id we reported on: {last_airflow_run_id}")

    if next_remote_run := poll_next_remote_run(
        api=SQLMeshEnterpriseAirflow(conn_id=conn_id).api,
        environment=environment,
        last_run_id=last_airflow_run_id,
        logger=logger,
    ):
        # We havent reported on this run yet, let's do it
        ti.xcom_push("run_id", next_remote_run.run_id)
        return True

    return False


def _report(conn_id: str, run_id: str, node_name: str) -> None:
    """
    Intended to be called by a PythonOperator to report on the status of a task in the remote run
    """
    import logging

    logger = logging.getLogger(__name__)

    api = SQLMeshEnterpriseAirflow(conn_id=conn_id).api

    if not run_id:
        raise AirflowFailException(
            "Unable to fetch run_id that should have been populated by the sensor task"
        )

    result = poll_until_remote_task_complete(
        api=api, run_id=run_id, node_name=node_name, logger=logger
    )

    if result.status == V1Status.FAILED:
        raise AirflowFailException()
    elif result.status == V1Status.SKIPPED:
        raise AirflowSkipException()


class SQLMeshEnterpriseAirflow:
    """
    Generate an Airflow DAG based on a to Tobiko Cloud project

    Usage:

    ```python
    from tobikodata.sqlmesh_enterprise.intergrations.airflow import SQLMeshEnterpriseAirflow

    first_task, last_task, dag = SQLMeshEnterpriseAirflow().create_cadence_dag()

    # from here, you can add tasks to run before the first task and after the last task like so:
    extra_task = EmptyOperator()
    last_task >> extra_task
    ```
    """

    def __init__(self, conn_id: str = "tobiko_cloud"):
        """
        :conn_id - Airflow connection ID containing the Tobiko Cloud connection details

        When using API Token auth, the connection should be set up like so:

        - type: http
          host: https://cloud.tobikodata.com/your/project/root
          password: <tobiko cloud token>

        If using OAuth, the connection should be set up like so:

        - type: http
          host: https://cloud.tobikodata.com/your/project/root
          login: <oauth client id>
          password: <oauth client secret>
        """
        self.conn_id = conn_id

    @cached_property
    def config(self) -> Connection:
        # will raise AirflowNotFoundException if the user has not created conn_id
        return Connection.get_connection_from_secrets(conn_id=self.conn_id)

    @property
    def api(self) -> V1ApiClient:
        client_kwargs: t.Dict[str, t.Any] = {}

        # if both login and password are defined, assume oauth
        if (login := self.config.login) and (password := self.config.password):
            client_kwargs["oauth_client_id"] = login
            client_kwargs["oauth_client_secret"] = password
        # otherwise, assume token auth
        else:
            client_kwargs["token"] = self.config.password

        return V1ApiClient.create(base_url=self.config.host, **client_kwargs)

    def create_cadence_dag(
        self,
        environment: str = "prod",
        dag_kwargs: t.Dict[str, t.Any] = {},
        common_task_kwargs: t.Dict[str, t.Any] = {},
        sensor_task_kwargs: t.Dict[str, t.Any] = {},
        report_task_kwargs: t.Dict[str, t.Any] = {},
    ) -> t.Tuple[BaseOperator, BaseOperator, DAG]:
        env = self.api.dags.get_dag_for_environment(environment)
        if not env:
            raise AirflowNotFoundException(
                f"The environment '{environment}' is not present in Tobiko Cloud. Has a plan been run on it yet?"
            )

        dag_kwargs.setdefault("dag_id", f"{self.conn_id}_{environment}")
        dag_kwargs.setdefault(
            "description", f"SQLMesh cadence run for the '{environment}' environment"
        )
        dag_kwargs.setdefault("start_date", env.start_at)
        dag_kwargs.setdefault("schedule", env.schedule_cron)
        dag_kwargs.setdefault("catchup", False)
        dag_kwargs.setdefault("max_active_runs", 1)

        with DAG(
            **dag_kwargs,
        ) as dag:
            sensor_task = self._create_wait_for_run_sensor_task(
                environment, **{**common_task_kwargs, **sensor_task_kwargs}
            )

            report_tasks = {
                n.name: (
                    n,
                    self._create_report_task(n, **{**common_task_kwargs, **report_task_kwargs}),
                )
                for n in env.nodes
            }

            for node, task in report_tasks.values():
                for parent_name in node.parent_names:
                    _, parent_task = report_tasks[parent_name]
                    parent_task >> task

            join_task = self._create_synchronisation_point_task(**common_task_kwargs)

            tasks_with_no_parents = [
                task for _, task in report_tasks.values() if not task.upstream_task_ids
            ]
            tasks_with_no_children = [
                task for _, task in report_tasks.values() if not task.downstream_task_ids
            ]

            for task in tasks_with_no_parents:
                sensor_task >> task

            for task in tasks_with_no_children:
                task >> join_task

            return sensor_task, join_task, dag

    def _create_wait_for_run_sensor_task(
        self, environment: str, **task_kwargs: t.Any
    ) -> PythonSensor:
        return PythonSensor(
            task_id="wait_until_ready",
            python_callable=_wait_until_next_remote_run,
            op_kwargs={"conn_id": self.conn_id, "environment": environment},
            poke_interval=5,  # poll every 5 seconds
            **task_kwargs,
        )

    def _create_report_task(self, node: V1DagNode, **report_task_kwargs: t.Any) -> PythonOperator:
        task_id = node.name.replace('"', "")

        return PythonOperator(
            task_id=task_id,
            task_display_name=exp.to_table(node.name).name,
            python_callable=_report,
            op_kwargs={
                "conn_id": self.conn_id,
                "run_id": '{{ ti.xcom_pull(key="run_id") }}',
                "node_name": node.name,
            },
            trigger_rule=TriggerRule.ALL_DONE,  # to enable these tasks to reflect the remote state regardless of the state of upstream tasks in Airflow
            **report_task_kwargs,
        )

    def _create_synchronisation_point_task(self, **task_kwargs: t.Any) -> EmptyOperator:
        # this is just a synchronisation point so that a user can tack on extra tasks once all snapshots finish,
        # even if there are a bunch running in parallel because they dont depnd on each other
        return EmptyOperator(task_id="finish", trigger_rule=TriggerRule.ALL_DONE, **task_kwargs)
