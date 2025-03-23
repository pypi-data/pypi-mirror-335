# mypy: disable-error-code="override"
from typing import List, Optional

import aiohttp

from klu.common.client import KluClientBase
from klu.feedback.constants import FEEDBACK_ENDPOINT
from klu.feedback.models import Feedback
from klu.utils.dict_helpers import dict_no_empty
from klu.utils.paginator import Paginator


class FeedbackClient(KluClientBase):
    VALUE_MAPPING = {"Negative": "1", "Positive": "2"}

    def __init__(self, api_key: str):
        super().__init__(api_key, FEEDBACK_ENDPOINT, Feedback)
        self._paginator = Paginator(FEEDBACK_ENDPOINT)

    async def list(self) -> List[Feedback]:
        """
        Retrieves all feedback for a user represented by the used API_KEY.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Returns (List[Action]): An array of all feedback
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_all(client)

            return [Feedback._from_engine_format(action) for action in response]

    async def fetch_single_page(self, page_number, limit: int = 100) -> List[Feedback]:
        """
        Retrieves a single page of feedback.
        Can be used to fetch a specific page of feedback provided a certain per_page config.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Args:
            page_number (int): Number of the page to fetch
            limit (int): Number of instances to fetch per page. Defaults to 100

        Returns:
            An array of feedback fetched for a queried page. Empty if queried page does not exist
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_single_page(
                client, page_number, limit=limit
            )

            return [Feedback._from_engine_format(action) for action in response]

    async def fetch_next_page(
        self, limit: int = 100, offset: Optional[int] = None
    ) -> List[Feedback]:
        """
        Retrieves the next page of feedback. Can be used to fetch a flexible number of pages starting.
        The place to start from can be controlled by the offset parameter.
        After using this method, we suggest to call `reset_pagination` method to reset the page cursor.

        Args:
            limit (int): Number of instances to fetch per page. Defaults to 100
            offset (int): The number of instances to skip. Can be used to query the pages of feedback skipping certain number of instances.

        Returns:
            An array of feedback fetched for a queried page. Empty if the end was reached at the previous step.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_next_page(
                client, limit=limit, offset=offset
            )

            return [Feedback._from_engine_format(action) for action in response]

    async def reset_pagination(self):
        self._paginator = Paginator(FEEDBACK_ENDPOINT)

    async def get(self, guid: str) -> Feedback:
        """
        Retrieves feedback.

        Args:
            guid (str): feedback guid.

        Returns:
            A Feedback object.
        """
        return await super().get(guid)

    async def update(
        self,
        guid: str,
        type: Optional[str] = None,
        value: Optional[str] = None,
        source: Optional[str] = None,
        created_by: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Feedback:
        """
        Update feedback information.

        Args:
            guid (str): ID of a feedback object to update.
            type (str): Type of feedback
            value (str): Value of feedback
            source (str): Source of feedback
            created_by (str): User who created the feedback
            metadata (dict): Metadata of feedback

        Returns:
            Newly updated Feedback object
        """
        if type == 'rating' and value:
            value = self.VALUE_MAPPING.get(value, None)

        data = {
            "type": type,
            "value": value,
            "source": source,
            "created_by": created_by,
            "metadata": metadata,
        }
        return await super().update(**{"guid": guid, **dict_no_empty(data)})

    async def create(
        self,
        type: str,
        value: str,
        data_guid: int,
        created_by: str,
        metadata: Optional[dict] = None,
        source: str = 'api',
    ) -> Feedback:
        """
        Creates new feedback on a data point.

        Args:
            type (str): Type of feedback
            value (str): Value of feedback
            data_guid (int): ID of a data point to create feedback on
            created_by (str): User who created the feedback
            meta_data (dict): Metadata of feedback
            source (str): Source of feedback

        Returns:
            Created Feedback object
        """
        if type == 'rating':
            value = self.VALUE_MAPPING.get(value, value)
        return await super().create(
            type=type,
            value=value,
            data=data_guid,
            createdById=created_by,
            source=source,
            meta_data=metadata,
        )

    async def log(
        self,
        data_guid: str,
        rating: Optional[str] = None,
        correction: Optional[str] = None,
        issue: Optional[str] = None,
        action: Optional[str] = None,
        source: Optional[str] = None,
        created_by: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> List[Feedback]:
        """
        Create multiple pieces of feedback with one function call.

        Args:
            guid (str): ID of a feedback object to update.
            rating (str): Value of feedback
            correction (str): Value of feedback
            issue (str): Value of feedback
            action (str): Value of feedback
            source (str): Source of feedback
            created_by (str): User who created the feedback

        Returns:
            Newly created Feedback objects
        """
        feedback: List[Feedback] = []
        for type, value in {
            "rating": self.VALUE_MAPPING.get(rating, rating) if rating else None,
            "correction": correction,
            "issue": issue,
            "action": action,
        }.items():
            if value:
                feedback.append(
                    await super().create(
                        type=type,
                        value=value,
                        data=data_guid,
                        createdById=created_by,
                        source=source,
                        meta_data=metadata,
                    )
                )
        return feedback

    async def delete(self, guid: str) -> Feedback:
        """
        Deletes feedback.

        Args:
            guid (str): feedback guid.

        Returns:
            The deleted Feedback object.
        """
        return await super().delete(guid)
