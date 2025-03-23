# mypy: disable-error-code="override"
from typing import List, NoReturn, Optional

import aiohttp

from klu.common.client import KluClientBase
from klu.common.errors import NotSupportedError
from klu.utils.dict_helpers import dict_no_empty
from klu.utils.paginator import Paginator
from klu.workflows.constants import WORKFLOWS_ENDPOINT
from klu.workflows.models import (
    Workflow,
    WorkflowResponse,
    WorkflowRun,
    WorkflowRunResult,
    WorkflowRunResultDataset,
)


class WorkflowClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(
            api_key,
            WORKFLOWS_ENDPOINT,
            Workflow,
        )

    async def create(self) -> NoReturn:
        raise NotSupportedError()

    async def get(self, guid: str) -> Workflow:
        raise NotSupportedError()

    async def update(self) -> NoReturn:
        raise NotSupportedError()

    async def delete(self, guid: str) -> NoReturn:
        raise NotSupportedError()

    async def list(self) -> List[Workflow]:
        """
        Retrieves all workflows attached to a workspace.

        Returns:
            An array of all workflows
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await client.get(WORKFLOWS_ENDPOINT)

            return [Workflow._from_engine_format(workflow) for workflow in response]

    async def run(
        self,
        guid: str,
        input: dict,
        filter: Optional[str] = None,
        cache: Optional[bool] = None,
        metadata_filter: Optional[dict] = None,
    ) -> WorkflowResponse:
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            data = dict_no_empty(
                {
                    "input": input,
                    "filter": filter,
                    "cache": cache,
                    "metadata_filter": metadata_filter,
                }
            )
            response = await client.post(f"{WORKFLOWS_ENDPOINT}{guid}/trigger", data)

            return WorkflowResponse._create_instance(**response)

    async def get_runs(self, guid: str) -> List[WorkflowRun]:
        """
        Get the final result of all runs for a workflow.

        Args:
            guid: The guid of the workflow.

        Returns:
            A list of WorkflowRun objects representing the final result of each run.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await client.get(f"{WORKFLOWS_ENDPOINT}/{guid}/result")
            return [WorkflowRun._create_instance(**run) for run in response]

    async def get_run_result(self, guid: str, run_guid: str) -> WorkflowRunResult:
        """
        Get the final result of a run.

        Args:
            guid: The guid of the workflow.
            run_guid: The guid of the run.

        Returns:
            The final result of the run.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await client.get(
                f"{WORKFLOWS_ENDPOINT}/{guid}/result/{run_guid}"
            )
            return response

    async def get_run_result_dataset(
        self, guid: str, run_guid: str
    ) -> WorkflowRunResultDataset:
        """
        Get the result of a run including individual block responses.

        Args:
            guid: The guid of the workflow.
            run_guid: The guid of the run.

        Returns:
            The result of the run including individual block responses.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await client.get(
                f"{WORKFLOWS_ENDPOINT}/{guid}/result/{run_guid}/dataset"
            )
            return WorkflowRunResultDataset._create_instance(**response)
