# mypy: disable-error-code="override"
from typing import List, Optional

import aiohttp

from klu.common.client import KluClientBase
from klu.data.models import Data
from klu.dataset.constants import (
    DATASET_BY_APP_ENDPOINT,
    DATASET_DATA_ENDPOINT,
    DATASET_ENDPOINT,
)
from klu.dataset.models import Dataset
from klu.utils.paginator import Paginator


class DatasetClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, DATASET_ENDPOINT, Dataset)
        self._paginator = Paginator(DATASET_ENDPOINT)

    async def create(
        self, name: str, description: str, app: str, data: Optional[List] = None
    ) -> Dataset:
        """
        Creates a new data set using data guids.

        Args:
            name (str): Name of the data set.
            description (str): Description of the data set.
            app (str): guid of the app to which the data set belongs.
            data (list, optional): List of guids of data points to be added to the data set. Defaults to None.

        Returns:
            Dataset: A new data set object.
        """
        return await super().create(
            name=name, description=description, app=app, data=data, url=DATASET_ENDPOINT
        )

    async def list(self) -> List[Dataset]:
        """
        Retrieves all data sets in.

        Returns:
            A list of Dataset objects.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_all(client)

            return [Dataset._from_engine_format(action) for action in response]

    async def get(self, guid: str) -> Dataset:
        """
        Retrieves Data set from a guid.

        Args:
            guid (str): guid of a dataset object to fetch.

        Returns:
            A Dataset object.
        """
        return await super().get(guid)

    async def get_data(self, guid: str):
        """
        Retrieves data from a data set.

        Args:
            guid (str): guid of the data set.

        Returns:
            A list of data objects.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)

            response = await client.get(DATASET_DATA_ENDPOINT.format(guid=guid))
            return [Data._from_engine_format(datum) for datum in response]

    async def add_data(self, guid: str, data: List[str]):
        """
        Adds data to a data set.

        Args:
            guid (str): guid of the data set.
            data (list): List of guids of data points to be added to the data set.

        Returns:
            A list of Data objects.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)

            response = await client.put(
                DATASET_DATA_ENDPOINT.format(guid=guid), {"data": data}
            )
            return [Data._from_engine_format(datum) for datum in response]

    async def update(self) -> Dataset:
        """ """
        raise NotImplementedError

    async def delete(self, guid: str) -> Dataset:
        """
        Delete an existing data set.

        Args:
            guid (str): The guid of the data set to delete.

        Returns:
            The deleted Dataset object.
        """
        return await super().delete(guid)
