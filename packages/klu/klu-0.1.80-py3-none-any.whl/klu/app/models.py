"""
This module provides data models for the App.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from klu.common.models import BaseEngineModel


@dataclass
class App(BaseEngineModel):
    """
    This class represents the App data model returned from the Klu engine
    """

    id: int
    guid: str
    name: str
    enabled: bool

    workspace_id: int
    created_by_id: str

    description: Optional[str]
    deleted: Optional[bool] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None

    def __repr__(self):
        return self.generate_repr()

    @classmethod
    def _from_engine_format(cls, data: dict) -> "App":
        return cls._create_instance(**data)

    def _to_engine_format(self) -> dict:
        base_dict = asdict(self)

        return {**base_dict}
