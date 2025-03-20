import time
import typing as t
from dataclasses import dataclass
from logging import Logger

from pydantic import HttpUrl

from tobikodata.http_client import V1ApiClient
from tobikodata.http_client.api_models.v1.common import V1Status
from tobikodata.http_client.api_models.v1.evaluations import V1RunEvaluation
from tobikodata.http_client.api_models.v1.runs import V1Run


@dataclass
class RemoteTaskResult:
    status: V1Status
    run: V1Run
    evaluations: t.List[V1RunEvaluation]
    error_message: t.Optional[str] = None

    @property
    def last_evaluation(self) -> t.Optional[V1RunEvaluation]:
        try:
            return self.evaluations[-1]
        except IndexError:
            return None

    @property
    def link(self) -> t.Optional[HttpUrl]:
        if evaluation := self.last_evaluation:
            return evaluation.link
        return None

    @property
    def log_link(self) -> t.Optional[HttpUrl]:
        if evaluation := self.last_evaluation:
            return evaluation.log_link
        return None


def poll_next_remote_run(
    api: V1ApiClient, environment: str, last_run_id: t.Optional[str], logger: Logger
) -> t.Optional[V1Run]:
    logger.info(f"Fetching last remote run for environment: {environment}")
    last_remote_run = api.runs.get_last_run_for_environment(environment=environment)

    if last_remote_run:
        logger.info(f"Last local run: {last_run_id}")
        logger.info(f"Last run in Tobiko Cloud: {last_remote_run.run_id}")

        if last_remote_run.run_id != last_run_id:
            logger.info(f"Reporting on new remote run: {last_remote_run.run_id}")
            logger.info(f"View realtime output on Tobiko Cloud: {last_remote_run.link}")
            return last_remote_run
        else:
            logger.info(
                f"We have already reported on run '{last_remote_run.run_id}'; waiting for new run"
            )
    else:
        logger.warning(f"No runs in Tobiko Cloud for environment: {environment}")

    return None


def poll_until_remote_task_complete(
    api: V1ApiClient, run_id: str, node_name: str, logger: Logger
) -> RemoteTaskResult:
    logger.info(f"Run: '{run_id}'; Node: '{node_name}'")

    remote_run = api.runs.get_run_by_id(run_id)
    if not remote_run:
        raise Exception(f"Run with id {run_id} does not exist in Tobiko Cloud")

    def _wait_until_ended() -> t.Optional[t.List[V1RunEvaluation]]:
        # block until evaluation has ended which means we can mark this task as complete and move on
        # there isnt always anything to evaluate either (eg a model with a daily cadence will only get evaluated once per day even if we are running every 5mins)
        while True:
            # an evaluation is created per batch, meaning there can be multiple evaluation records for each snapshot in the run
            if our_evaluations := api.runs.get_evaluations_for_node(run_id, node_name):
                complete = [e for e in our_evaluations if e.end_at]
                incomplete = [e for e in our_evaluations if e not in complete]
                if incomplete:
                    # check if the run has actually finished. if the remote scheduler crashes, sometimes the evaluation record isnt updated
                    # to have an end_at (and thus is considered incomplete) but the run record is marked as completed with an error message
                    if remote_run.end_at:
                        if remote_run.error_message:
                            logger.error(f"Run '{run_id}' has failed remotely with:")
                            logger.error(remote_run.error_message)
                            raise Exception(
                                f"Run '{run_id}' failed remotely. View it in Tobiko Cloud: {remote_run.link}"
                            )

                        return None
                    else:
                        logger.info(
                            f"{len(complete)}/{len(our_evaluations)} evaluations have completed for this snapshot; waiting"
                        )
                        time.sleep(5)
                        continue

                return complete

            return None

    if complete_evaluations := _wait_until_ended():
        any_failed = False
        last_error_message: t.Optional[str] = None
        for evaluation in complete_evaluations:
            if evaluation.error_message:
                logger.error(f"Evaluation failed: {evaluation.error_message}")
                logger.error(f"View more information in Tobiko Cloud: {evaluation.link}")
                any_failed = True
                last_error_message = evaluation.error_message
            else:
                logger.info("Evaluation completed successfully")
                logger.info(f"View the log output in Tobiko Cloud: {evaluation.log_link}")

        status = V1Status.FAILED if any_failed else V1Status.SUCCESS
        return RemoteTaskResult(
            status=status,
            error_message=last_error_message,
            run=remote_run,
            evaluations=complete_evaluations,
        )
    else:
        logger.info("No evaluation record for this model; skipping")
        return RemoteTaskResult(status=V1Status.SKIPPED, run=remote_run, evaluations=[])
