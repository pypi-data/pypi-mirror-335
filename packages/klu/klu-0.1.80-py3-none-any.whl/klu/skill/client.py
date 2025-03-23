# mypy: disable-error-code="override"
from typing import List, NoReturn

import aiohttp

from klu.common.client import KluClientBase
from klu.common.errors import NotSupportedError
from klu.skill.constants import SKILLS_ENDPOINT
from klu.skill.models import Skill
from klu.utils.paginator import Paginator


class SkillsClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(
            api_key,
            SKILLS_ENDPOINT,
            Skill,
        )
        self._paginator = Paginator(SKILLS_ENDPOINT)

    async def create(self) -> NoReturn:
        raise NotSupportedError()

    async def get(self, guid: str) -> Skill:
        """
        Retrieves skill

        Args:
            guid (str): guid of a skill to fetch

        Returns:
            Skill object
        """
        return await super().get(guid)

    async def update(self) -> NoReturn:
        raise NotSupportedError()

    async def delete(self, guid: str) -> Skill:
        """
        Delete skill

        Args:
            guid (str): guid of the skill you want to delete

        Returns:
            Deleted Skill object
        """
        return await super().delete(guid)

    async def list(self) -> List[Skill]:
        """
        Retrieves all skills.

        Returns:
            A list of Skill objects.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_all(client)

            return [Skill._from_engine_format(skill) for skill in response]

    async def reset_pagination(self):
        self._paginator = Paginator(SKILLS_ENDPOINT)
