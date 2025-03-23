"""
This module provides data models for the Session.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from klu.common.models import BaseDataClass, BaseEngineModel


@dataclass
class Workflow(BaseEngineModel):
    """
    This class represents the Workflow data returned from the Klu engine
    """

    slug: str
    guid: str
    name: str
    app: str
    raw_yaml: str
    trigger: str
    metadata: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __repr__(self):
        return self.generate_repr()

    @classmethod
    def _from_engine_format(cls, data: dict) -> "Workflow":
        return cls._create_instance(
            **{
                "updated_at": data.pop("updatedAt", None),
                "created_at": data.pop("createdAt", None),
            },
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

        base_dict.pop("updated_at", None)
        base_dict.pop("created_at", None)

        return base_dict


class WorkflowResponse(BaseDataClass):
    msg: str
    status: str
    blocks: List[dict]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def _create_instance(cls, **kwargs):
        instance = cls.__new__(cls)
        instance._init_with_base_class(**kwargs)
        return instance


class WorkflowRunResultDataset(BaseDataClass):
    final: Any
    blocks: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def _create_instance(cls, **kwargs):
        instance = cls.__new__(cls)
        instance._init_with_base_class(**kwargs)
        return instance


class WorkflowRunResult(BaseDataClass):
    result: Any

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def _create_instance(cls, **kwargs):
        instance = cls.__new__(cls)
        instance._init_with_base_class(**kwargs)
        return instance


class WorkflowRun(BaseDataClass):
    """
    This class represents the Run data returned from the Klu engine
    """

    guid: str
    created_at: str
    updated_at: str
    workflow: str  # guid
    meta_data: Optional[Any] = None

    def __repr__(self):
        return self.generate_repr()

    @classmethod
    def _create_instance(cls, **kwargs):
        instance = cls.__new__(cls)
        instance._init_with_base_class(**kwargs)
        return instance
