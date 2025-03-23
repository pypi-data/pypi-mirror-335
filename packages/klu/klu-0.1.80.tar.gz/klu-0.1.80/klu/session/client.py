# mypy: disable-error-code="override"
from typing import List, NoReturn, Optional

import aiohttp

from klu.common.client import KluClientBase
from klu.common.errors import NotSupportedError
from klu.session.constants import SESSION_ENDPOINT
from klu.session.models import Session
from klu.utils.paginator import Paginator


class SessionClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, SESSION_ENDPOINT, Session)
        self._paginator = Paginator(SESSION_ENDPOINT)

    async def create(
        self, action: str, name: Optional[str] = None, extUserId: Optional[str] = None
    ) -> Session:
        """
        Creates a session based on the data provided.

        Args:
            action (str): guid of the action to which the session belongs.
            name (Optional[str]): Name of the session. If not provided will be left blank.

        Returns:
            A newly created Session object.
        """
        return await super().create(action=action, name=name, extUserId=extUserId)

    async def list(self) -> List[Session]:
        """
        Retrieves all actions for a user represented by the used API_KEY.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Returns (List[Session]): An array of all sessions
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_all(client)

            return [Session._from_engine_format(session) for session in response]

    async def fetch_single_page(self, page_number, limit: int = 100) -> List[Session]:
        """
        Retrieves a single page of session.
        Can be used to fetch a specific page of actions provided a certain per_page config.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Args:
            page_number (int): Number of the page to fetch
            limit (int): Number of instances to fetch per page. Defaults to 100

        Returns:
            An array of sessions fetched for a queried page. Empty if queried page does not exist
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_single_page(
                client, page_number, limit=limit
            )

            return [Session._from_engine_format(action) for action in response]

    async def fetch_next_page(
        self, limit: int = 100, offset: Optional[int] = None
    ) -> List[Session]:
        """
        Retrieves the next page of session. Can be used to fetch a flexible number of pages starting.
        The place to start from can be controlled by the offset parameter.
        After using this method, we suggest to call `reset_pagination` method to reset the page cursor.

        Args:
            limit (int): Number of instances to fetch per page. Defaults to 100
            offset (int): The number of instances to skip. Can be used to query the pages of actions skipping certain number of instances.

        Returns:
            An array of sessions fetched for a queried page. Empty if the end was reached at the previous step.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_next_page(
                client, limit=limit, offset=offset
            )

            return [Session._from_engine_format(action) for action in response]

    async def reset_pagination(self):
        self._paginator = Paginator(SESSION_ENDPOINT)

    async def get(self, guid: str) -> Session:
        """
        Retrieves session information based on the unique Session guid

        Args:
            guid (str): guid of a session to fetch.

        Returns:
            Session object
        """
        return await super().get(guid)

    async def update(self) -> NoReturn:
        raise NotSupportedError()

    async def delete(self, guid: str) -> Session:
        """
        Delete a session.

        Args:
            guid (str): Unique guid of a session to delete.

        Returns:
            Deleted Session object
        """
        return await super().delete(guid)
