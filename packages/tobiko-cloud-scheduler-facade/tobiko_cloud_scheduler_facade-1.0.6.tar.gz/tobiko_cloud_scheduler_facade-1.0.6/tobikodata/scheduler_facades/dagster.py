import re
import typing as t
from functools import cached_property

from dagster import (
    AssetCheckResult,
    AssetChecksDefinition,
    AssetKey,
    AssetMaterialization,
    AssetSpec,
    ConfigurableResource,
    DagsterInstance,
    DefaultSensorStatus,
    Definitions,
    DependencyDefinition,
    Failure,
    GraphDefinition,
    In,
    JobDefinition,
    MetadataValue,
    Nothing,
    OpDefinition,
    OpExecutionContext,
    Output,
    RunRequest,
    SensorDefinition,
    SensorEvaluationContext,
    SkipReason,
    asset_check,
    job,
    op,
    sensor,
)
from dagster._core.definitions import AssetCheckEvaluation
from dagster._core.definitions.utils import INVALID_NAME_CHARS
from dagster_graphql import DagsterGraphQLClient
from sqlglot import exp

from tobikodata.http_client import V1ApiClient
from tobikodata.http_client.api_models.v1.common import V1Status
from tobikodata.http_client.api_models.v1.dags import (
    V1Dag,
    V1DagNode,
    V1DagNodeSourceType,
    V1DagNodeType,
)
from tobikodata.http_client.api_models.v1.evaluations import (
    V1EvaluationBase,
    V1RunEvaluation,
)
from tobikodata.scheduler_facades.common import (
    poll_next_remote_run,
    poll_until_remote_task_complete,
)

INVALID_NAME_CHARS_REGEX = re.compile(INVALID_NAME_CHARS)

# map of SQLMesh source types to Dagster "compute kinds": https://docs.dagster.io/concepts/metadata-tags/kind-tags#kind-tags
SOURCE_TYPE_TO_COMPUTE_KIND = {
    V1DagNodeSourceType.SQL: "sql",
    V1DagNodeSourceType.PYTHON: "python",
    V1DagNodeSourceType.SEED: "seed",
    V1DagNodeSourceType.AUDIT: "sql",
    V1DagNodeSourceType.EXTERNAL: "table",
}

ENVIRONMENT_TAG = "tobiko/environment"


class TobikoCloudResource(ConfigurableResource):
    url: str
    token: t.Optional[str]
    oauth_client_id: t.Optional[str]
    oauth_client_secret: t.Optional[str]

    # Path to Dagster UI GraphQL server
    # only required if you want to automatically refresh the code location to pick up new Models
    # (instead of manually clicking "Reload" in the Dagster UI)
    dagster_graphql_host: t.Optional[str] = None
    dagster_graphql_port: t.Optional[int] = None
    dagster_graphql_kwargs: t.Dict[str, t.Any] = {}

    @cached_property
    def api(self) -> V1ApiClient:
        return V1ApiClient.create(
            base_url=self.url,
            token=self.token,
            oauth_client_id=self.oauth_client_id,
            oauth_client_secret=self.oauth_client_secret,
        )

    @property
    def dagster(self) -> t.Optional[DagsterGraphQLClient]:
        if self.dagster_graphql_host:
            return DagsterGraphQLClient(
                hostname=self.dagster_graphql_host,
                port_number=self.dagster_graphql_port,
                **self.dagster_graphql_kwargs,
            )
        return None


class SQLMeshEnterpriseDagster:
    def __init__(
        self,
        url: str,
        token: t.Optional[str] = None,
        oauth_client_id: t.Optional[str] = None,
        oauth_client_secret: t.Optional[str] = None,
        dagster_graphql_host: t.Optional[str] = None,
        dagster_graphql_port: t.Optional[int] = None,
        dagster_graphql_kwargs: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self.conn = TobikoCloudResource(
            url=url,
            token=token,
            oauth_client_id=oauth_client_id,
            oauth_client_secret=oauth_client_secret,
            dagster_graphql_host=dagster_graphql_host,
            dagster_graphql_port=dagster_graphql_port,
            dagster_graphql_kwargs=dagster_graphql_kwargs or {},
        )

    def create_definitions(
        self,
        environment: str = "prod",
        asset_prefix: t.Optional[str] = None,
        enable_sensor_by_default: bool = True,
    ) -> Definitions:
        jobs = []
        assets: t.List[AssetSpec] = []
        asset_checks: t.List[AssetChecksDefinition] = []
        sensors = []
        if dag := self.conn.api.dags.get_dag_for_environment(environment):
            mirror_run_job = self._mirror_remote_run_job(dag, asset_prefix)
            initial_populate_job = self._initial_populate_job(environment, asset_prefix)
            jobs = [mirror_run_job, initial_populate_job]
            assets, asset_checks = self._asset_defintions(dag, asset_prefix)
            sensors = [
                self._remote_run_sensor(
                    environment,
                    initial_populate_job=initial_populate_job,
                    mirror_run_job=mirror_run_job,
                    enable_by_default=enable_sensor_by_default,
                )
            ]

        return Definitions(
            jobs=jobs,
            assets=assets,
            asset_checks=asset_checks,
            sensors=sensors,
            resources={"tobiko_cloud": self.conn},
        )

    def _parts(self, node_name: str, prefix: t.Optional[str]) -> t.List[str]:
        parsed_name = exp.to_table(node_name)
        key_parts = []
        if prefix:
            key_parts.append(prefix)
        if catalog := parsed_name.catalog:
            key_parts.append(catalog)
        if db := parsed_name.db:
            key_parts.append(db)
        if name := parsed_name.name:
            key_parts.append(name)
        return key_parts

    def _asset_key(self, node_name: str, prefix: t.Optional[str] = None) -> AssetKey:
        # AssetKey's allow dashes so we dont strip them to better reflect the actual model names
        return AssetKey(self._parts(node_name, prefix))

    def _op_name(self, node_name: str, prefix: t.Optional[str] = None) -> str:
        return "_".join([self._make_valid_dagster_name(p) for p in self._parts(node_name, prefix)])

    def _make_valid_dagster_name(self, name: str) -> str:
        """
        Dagster will throw an error if you try to create an @op or a @graph that doesnt match its name regex
        In practice, the name must only have alphanumeric and _ characters
        ref: https://github.com/dagster-io/dagster/blob/73ed07a1afa9422a9715faeb5e8d14594ff26d3b/python_modules/dagster/dagster/_core/definitions/utils.py#L66
        """
        return INVALID_NAME_CHARS_REGEX.sub("", name)

    def _create_asset_check_definition(
        self, asset_key: AssetKey, check_name: str
    ) -> AssetChecksDefinition:
        @asset_check(
            asset=asset_key,
            name=check_name,
        )
        def _check() -> AssetCheckResult:
            # placeholder fn because we cant add the asset checks to AssetSpec
            # the actual check results get emitted when we fetch a remote evaluation (and it contains audit results)
            # returning None here indicates "skipped" if a user tries to execute this check manually from the UI
            return None  # type: ignore

        return _check

    def _asset_defintions(
        self, dag: V1Dag, asset_prefix: t.Optional[str]
    ) -> t.Tuple[t.List[AssetSpec], t.List[AssetChecksDefinition]]:
        assets = []
        asset_checks = []
        for node in dag.nodes:
            if node.type == V1DagNodeType.AUDIT:
                # standalone audits can cover multiple models
                # emit an AssetCheckDefinition for every model covered by the audit
                asset_checks.extend(
                    [
                        self._create_asset_check_definition(
                            self._asset_key(parent_name, asset_prefix), node.name
                        )
                        for parent_name in node.parent_names
                    ]
                )

            elif node.type == V1DagNodeType.MODEL:
                asset_key = self._asset_key(node.name, asset_prefix)
                description = f"{node.description}\n\n[View in Tobiko Cloud]({str(node.link)})"
                kinds = (
                    {SOURCE_TYPE_TO_COMPUTE_KIND[node.source_type]}
                    if node.source_type in SOURCE_TYPE_TO_COMPUTE_KIND
                    else None
                )

                assets.append(
                    AssetSpec(
                        key=asset_key,
                        deps=[self._asset_key(n, asset_prefix) for n in node.parent_names],
                        description=description,
                        kinds=kinds,
                        tags={ENVIRONMENT_TAG: dag.environment},
                    )
                )

                asset_checks.extend(
                    [
                        self._create_asset_check_definition(
                            asset_key=asset_key, check_name=audit_name
                        )
                        for audit_name in node.audit_names
                    ]
                )

        return assets, asset_checks

    def _poll_node(self, dag: V1Dag, node: V1DagNode, prefix: t.Optional[str]) -> OpDefinition:
        @op(
            name=self._op_name(node.name, prefix),
            ins={self._op_name(p, prefix): In(Nothing) for p in node.parent_names},
        )
        def _poll(
            context: OpExecutionContext, tobiko_cloud: TobikoCloudResource
        ) -> t.Iterator[t.Union[Output[V1Status], Failure]]:
            # the remote run_id should have been populated by the sensor task
            # unless this was triggered manually by someone manually running the job
            remote_run_id = context.get_tag("dagster/run_key")
            if not remote_run_id:
                context.log.warning(
                    "No remote run id has been set on this run - perhaps it was triggered manually?"
                )
                if last_run := tobiko_cloud.api.runs.get_last_run_for_environment(dag.environment):
                    remote_run_id = last_run.run_id
                    context.log.warning(f"Using the most recent remote run id: {last_run.run_id}")
                else:
                    raise Failure("No remote runs to report on; cannot materialize asset")

            result = poll_until_remote_task_complete(
                api=tobiko_cloud.api, run_id=remote_run_id, node_name=node.name, logger=context.log
            )
            if result.status == V1Status.FAILED:
                yield Failure(
                    description=f"Task {node.name} failed remotely. View logs at {result.log_link}",
                    allow_retries=False,
                )

            if result.last_evaluation:
                # todo: handle if the DAG node is an Audit node (Standalone audit)
                # standalone audits dont seem to get an evaluation_id ?
                self._register_remote_evaluation(
                    context.instance, self._asset_key(node.name, prefix), result.last_evaluation
                )

            yield Output(result.status)

        return _poll

    def _mirror_remote_run_job(self, dag: V1Dag, prefix: t.Optional[str]) -> JobDefinition:
        """
        This Job mirrors a remote run task-for-task and logs materialization / check events if the
        remote equivalent succeeded

        Note that we have to use the Job / Op API to keep the asset information up to date because our models are
        exposed as External Assets and thus dont contain a materialization function

        Note: this is deliberate. Registering models as normal Assets instead of External Assets is problematic, because it:
            - enables a "Materialize" button in the UI that a user might click expecting something to happen (there is no way currently to trigger a model evaluation on-demand in Tobiko Cloud)
            - there is no way to "skip" materializing an Asset from within its materialization function (which would be the function checking the remote status).
              Once the materialization function exits without throwing an Exception, Dagster considers the Asset materialized. If you throw an Exception, Dagster considers it a failure.
            - Dagster errors if you dont emit AssetCheckResults matching the checks attached to the Asset when the materialization function runs.
              But not all audits are run all the time, so being forced to emit something just overrides the status to "skipped" or updates the check
              "passed" timestamp even though no actual check was performed
        """

        graph = GraphDefinition(
            name=f"tobiko_cloud_mirror_run_{dag.environment}",
            node_defs=[self._poll_node(dag, node, prefix) for node in dag.nodes],
            dependencies={
                self._op_name(node.name, prefix): {
                    self._op_name(p, prefix): DependencyDefinition(self._op_name(p, prefix))
                    for p in node.parent_names
                }
                for node in dag.nodes
            },
        )

        return graph.to_job()

    def _initial_populate_job(self, environment: str, prefix: t.Optional[str]) -> JobDefinition:
        """
        This job is to refresh the "current state" of the models (assets) from Tobiko Cloud.

        This is mainly for performing an initial sync or to sync the current state of an environment to Dagster without waiting for a cadence run
        (which itself might only touch a subset of models)

        Unfortunately we cannot yet have accurate materialization timestamps, see https://github.com/dagster-io/dagster/issues/19976
        """

        @op()
        def populate_asset_info(
            context: OpExecutionContext, tobiko_cloud: TobikoCloudResource
        ) -> Output:
            context.log.info(
                f"Populating initial asset state for Tobiko Cloud environment: {environment}"
            )

            for evaluation in tobiko_cloud.api.evaluations.get_latest_evaluations_for_environment(
                environment
            ):
                if not evaluation.complete:
                    context.log.warning(
                        f"Skipping evaluation for {evaluation.node_name} (evaluation id: {evaluation.evaluation_id}) that is still in progress"
                    )
                    continue

                context.log.info(
                    f"Emitting information for {evaluation.node_name} (including {len(evaluation.audits)} audits)"
                )

                self._register_remote_evaluation(
                    context.instance, self._asset_key(evaluation.node_name, prefix), evaluation
                )

                context.log.info(
                    f"View model overview for {evaluation.node_name} in Tobiko Cloud: {evaluation.link}"
                )

            return Output(Nothing)

        @job(name=f"tobiko_cloud_sync_{environment}")
        def _job() -> None:
            populate_asset_info()

        return _job

    def _reload_code_location(
        self, ctx: SensorEvaluationContext, tobiko_cloud: TobikoCloudResource
    ) -> None:
        """
        This establishes a link back to the Dagster Werbserver to trigger a code location reload which will pick up new models.

        If we trigger a reload in this process via something like:
        > ctx.code_location_origin.reload_location(ctx.instance)

        Then the reloaded info is only visible to this process and the Dagster Webserver never picks it up.
        The reload needs to be triggered by the Dagster Webserver so it can update its local state with the new assets / job steps
        """
        if code_location_origin := ctx.code_location_origin:
            name = code_location_origin.location_name

            if code_location_origin.is_reload_supported:
                # We have to establish a connection back to the Dagster Webserver in order to make it pick up new Asset definitions
                # otherwise, we just reload within this process and the Dagster Webserver is never updated
                if dagster := tobiko_cloud.dagster:
                    ctx.log.info(
                        f"Reloading code location '{name}' to pick up any new Model definitions"
                    )
                    dagster.reload_repository_location(name)
                    ctx.log.info("Reload complete")
                else:
                    ctx.log.info(
                        f"No dagster_graphql_host has been specified; skipping automatic asset reload. You will need to click 'Reload' against the code location '{name}' manually from within the Dagster UI to pick up new models"
                    )
            else:
                ctx.log.warning(
                    f"Code location {name} does not support reload. This means that any new SQLMesh models will not be picked up"
                )
                ctx.log.warning(
                    "Please use a Code Location type that can be reloaded. For more information, see the Dagster documentation: https://docs.dagster.io/guides/deploy/code-locations/"
                )

    def _remote_run_sensor(
        self,
        environment: str,
        initial_populate_job: JobDefinition,
        mirror_run_job: JobDefinition,
        enable_by_default: bool,
    ) -> SensorDefinition:
        """
        This sensor polls Tobiko Cloud to pick up new cadence runs. If it finds one, it triggers the mirror job.

        It's also responsible for automatically triggering a sync in a new deployment.

        Note that it is deliberately enabled by default for a smoother user experience
        """

        @sensor(
            name=f"tobiko_cloud_track_{environment}",
            minimum_interval_seconds=30,
            default_status=DefaultSensorStatus.RUNNING
            if enable_by_default
            else DefaultSensorStatus.STOPPED,
            jobs=[initial_populate_job, mirror_run_job],
        )
        def _sensor(
            ctx: SensorEvaluationContext, tobiko_cloud: TobikoCloudResource
        ) -> t.Iterator[t.Union[RunRequest, SkipReason]]:
            # first run, sync all assets with tcloud because a cadence run doesnt necessarily materialize everything
            if not ctx.cursor:
                ctx.log.info(
                    "This is the first run; triggering initial model sync from Tobiko Cloud"
                )
                yield RunRequest(run_key="__initial_sync__", job_name=initial_populate_job.name)
                ctx.update_cursor("__initial_sync_complete__")
            elif next_run := poll_next_remote_run(
                api=tobiko_cloud.api,
                environment=environment,
                last_run_id=ctx.cursor,
                logger=ctx.log,
            ):
                # first, reload the code location incase there are new models that we need AssetSpec's for
                self._reload_code_location(ctx, tobiko_cloud)

                # then, trigger a run of the mirror job
                yield RunRequest(run_key=next_run.run_id, job_name=mirror_run_job.name)
                ctx.update_cursor(next_run.run_id)
            else:
                yield SkipReason("No new remote runs")

        return _sensor

    def _register_remote_evaluation(
        self,
        dagster: DagsterInstance,
        asset_key: AssetKey,
        evaluation: t.Union[V1EvaluationBase, V1RunEvaluation],
    ) -> None:
        extra_metadata = {}
        if isinstance(evaluation, V1RunEvaluation):
            extra_metadata["Tobiko Cloud Run Id"] = evaluation.run_id

        dagster.report_runless_asset_event(
            AssetMaterialization(
                asset_key=asset_key,
                metadata={
                    **extra_metadata,
                    "Tobiko Cloud Evaluation Id": evaluation.evaluation_id,
                    "Log Link": MetadataValue.url(f"{evaluation.log_link}"),
                    "Materialization Timestamp": MetadataValue.timestamp(evaluation.end_at)
                    if evaluation.end_at
                    else "TODO: no end_at?",
                    "Evaluation Status": f"{evaluation.status}",
                },
            )
        )

        for audit in evaluation.audits:
            dagster.report_runless_asset_event(
                AssetCheckEvaluation(
                    asset_key=asset_key,
                    check_name=audit.name,
                    passed=audit.status == V1Status.SUCCESS,
                    metadata={
                        "Tobiko Cloud Evaluation Id": MetadataValue.text(evaluation.evaluation_id),
                        "Log Link": MetadataValue.url(f"{audit.log_link}"),
                        "Execution Timestamp": MetadataValue.timestamp(audit.execution_time),
                        "Interval Start Timestamp": MetadataValue.timestamp(audit.interval_start),
                        "Interval End Timestamp": MetadataValue.timestamp(audit.interval_end),
                    },
                )
            )
