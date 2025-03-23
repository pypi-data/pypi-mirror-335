# mypy: disable-error-code="override"
from typing import List, Optional

import aiohttp
from aiohttp import ClientResponseError

from klu.action.models import Action
from klu.app.constants import (
    APP_ACTIONS_ENDPOINT,
    APP_DATA_ENDPOINT,
    APP_ENDPOINT,
    DEFAULT_APPS_PAGE_SIZE,
)
from klu.app.errors import AppNotFoundError
from klu.app.models import App
from klu.common.client import KluClientBase
from klu.common.errors import InvalidUpdateParamsError, UnknownKluAPIError
from klu.data.models import Data
from klu.utils.dict_helpers import dict_no_empty
from klu.utils.paginator import Paginator


class AppsClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, APP_ENDPOINT, App)
        self._paginator = Paginator(APP_ENDPOINT)

    async def create(self, name: str, description: str) -> App:
        """
        Creates a new app instance.

        Args:
            name (str): Name of the new app.
            description (str): Description of the new app.

        Returns:
            App: Newly created App object.
        """
        return await super().create(
            name=name,
            description=description,
        )

    async def get(self, guid: str) -> App:
        """
        Retrieves an app and returns an app object

        Args:
            guid (str): guid of an app to fetch.

        Returns:
            App object
        """
        return await super().get(guid)

    async def update(
        self,
        guid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> App:
        """
        Update app metadata. At least one of the params has to be provided

        Args:
            guid (str): GUID of an app to fetch.
            name: Optional[str]. New app name
            description: Optional[str]. New app description

        Returns:
            Updated app object
        """

        if not name and not description:
            raise InvalidUpdateParamsError()

        return await super().update(
            **{
                "guid": guid,
                **dict_no_empty({"name": name, "description": description}),
            }
        )

    async def delete(self, guid: str) -> App:
        """
        Delete an existing app.

        Args:
            guid (str): The guid of the app to delete.

        Returns:
            The deleted app object.
        """
        return await super().delete(guid)

    async def get_data(self, guid: str) -> List[Data]:
        """
        Retrieves app data information based on the app guid.

        Args:
            guid (str): guid of an app to fetch data for. The one that was returned during the app creation

        Returns:
            An array of data objects, found by provided app guid.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.get(APP_DATA_ENDPOINT.format(id=guid))
                return [Data._from_engine_format(data) for data in response]
            except ClientResponseError as e:
                if e.status == 404:
                    raise AppNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)

    async def get_actions(self, guid: str) -> List[Action]:
        """
        Retrieves app actions information based on the app GUID.

        Args:
            guid (str): GUID of an app to fetch actions for. The one that was used during the app creation

        Returns:
            An array of actions, found by provided app id.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.get(APP_ACTIONS_ENDPOINT.format(id=guid))
                return [Action._from_engine_format(action) for action in response]
            except ClientResponseError as e:
                if e.status == 404:
                    raise AppNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)

    async def list(self) -> List[App]:
        """
        Retrieves all apps attached to a workspace.

        Returns:
            An array of all apps
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_all(client)

            return [App._from_engine_format(app) for app in response]

    async def fetch_single_page(
        self, page_number, limit: int = DEFAULT_APPS_PAGE_SIZE
    ) -> List[App]:
        """
        Retrieves a single page of apps.
        Can be used to fetch a specific page of apps provided a certain per_page config.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Args:
            page_number (int): Number of the page to fetch
            limit (int): Number of instances to fetch per page. Defaults to 50

        Returns:
            An array of apps fetched for a queried page. Empty if queried page does not exist
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_single_page(
                client, page_number, limit=limit
            )

            return [App._from_engine_format(app) for app in response]

    async def fetch_next_page(
        self, limit: int = DEFAULT_APPS_PAGE_SIZE, offset: Optional[int] = None
    ) -> List[App]:
        """
        Retrieves the next page of apps. Can be used to fetch a flexible number of pages starting.
        The place to start from can be controlled by the offset parameter.
        After using this method, we suggest to call `reset_pagination` method to reset the page cursor.

        Args:
            limit (int): Number of instances to fetch per page. Defaults to 50
            offset (int): The number of apps to skip. Can be used to query the pages of apps skipping certain number of instances.

        Returns:
            An array of apps fetched for a queried page. Empty if the end was reached at the previous step.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_next_page(
                client, limit=limit, offset=offset
            )

            return [App._from_engine_format(app) for app in response]

    async def reset_pagination(self):
        self._paginator = Paginator(APP_ENDPOINT)
