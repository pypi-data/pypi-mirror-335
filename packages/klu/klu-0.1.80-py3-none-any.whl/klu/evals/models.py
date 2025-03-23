"""
This module provides data models for the Data.
"""

from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from klu.common.models import BaseEngineModel


@dataclass
class Eval(BaseEngineModel):
    """
    This class represents the dataset reponse from the API.
    """

    guid: str
    name: str = ""
    description: str = ""
    app: str = ""
    created_by_id: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    dataset: Optional[Dict[str, Any]] = None

    def __repr__(self):
        return self.generate_repr()

    @classmethod
    def _from_engine_format(cls, data: dict) -> "Eval":
        return cls._create_instance(
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )
        return base_dict


@dataclass
class EvalType(BaseEngineModel):
    """
    This class represents the dataset reponse from the API.
    """

    guid: str
    name: str
    created_at: str
    updated_at: str
    type: Optional[str] = None
    owner: Optional[str] = None
    metadata: Optional[Any] = None
    eval_function: Optional[str] = None
    eval_run_type: Optional[str] = None

    def __repr__(self):
        return self.generate_repr()

    @classmethod
    def _from_engine_format(cls, data: dict) -> "EvalType":
        return cls._create_instance(
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )
        return base_dict


@dataclass
class EvalRun(BaseEngineModel):
    """
    This class represents the evaluation run item.
    """

    guid: str
    eval: str
    action: str
    version: str
    created_at: Any
    updated_at: Any
    created_by_id: str
    run_number: int
    deleted: bool
    metadata: Dict[str, Any]

    def __repr__(self):
        return self.generate_repr()

    @classmethod
    def _from_engine_format(cls, data: dict) -> "EvalRun":
        return cls._create_instance(
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )
        return base_dict
