"""
This module provides data models for the Action.
"""

from dataclasses import asdict, dataclass
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from klu.api.sse_client import OpenAISSEClient, SSEClient
from klu.common.models import (
    BaseDataClass,
    BaseEngineModel,
    PromptInput,
    TaskStatusEnum,
)


@dataclass
class ModelConfig(BaseDataClass):
    """
    This class represents the ModelConfig data model returned from the Klu engine
    """

    top_p: Optional[float] = 1
    temperature: Optional[float] = 0.5
    timeout: Optional[int] = 60
    num_retries: Optional[int] = 2
    stop_sequence: Optional[List[str]] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    max_response_length: Optional[int] = 1000
    seed: Optional[int] = None
    response_format: Optional[str] = None
    logit_bias: Optional[List] = None


@dataclass
class Action(BaseEngineModel):
    """
    This class represents the Action data model returned from the Klu engine
    """

    guid: str
    name: str
    app: str
    model: str
    action_type: str
    prompt: PromptInput
    system_message: Optional[str]
    description: Optional[str]
    model_config: Optional[ModelConfig]
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

    def __repr__(self):
        return self.generate_repr()

    @classmethod
    def _from_engine_format(cls, data: dict) -> "Action":
        model_config = data.pop("model_config", {})
        if model_config is None:
            model_config = {}
        mc_config = {
            "top_p": model_config.get("topP", None),
            "temperature": model_config.get("temperature", None),
            "timeout": model_config.get("timeout", None),
            "num_retries": model_config.get("numRetries", None),
            "stop_sequence": model_config.get("stopSequence", []),
            "presence_penalty": model_config.get("presencePenalty", None),
            "frequency_penalty": model_config.get("frequencyPenalty", None),
            "max_response_length": model_config.get("maxResponseLength", None),
            "seed": model_config.get("eed", None),
            "response_format": model_config.get("responseFormat", None),
            "logit_bias": model_config.get("logitBias", None),
        }
        data["model_config"] = ModelConfig(**mc_config)
        obj = cls._create_instance(
            **data,
        )
        return obj

    def _to_engine_format(self) -> dict:
        base_dict = asdict(self)
        model_config = base_dict.pop("model_config", None)
        return {
            "model_config": {
                "topP": model_config.top_p,
                "temperature": model_config.temperature,
                "timeout": model_config.timeout,
                "numRetries": model_config.num_retries,
                "stopSequence": model_config.stop_sequence,
                "presencePenalty": model_config.presence_penalty,
                "frequencyPenalty": model_config.frequency_penalty,
                "maxResponseLength": model_config.max_response_length,
                "seed": model_config.seed,
                "responseFormat": model_config.response_format,
                "logitBias": model_config.logit_bias,
            },
            **base_dict,
        }


@dataclass
class Version(BaseEngineModel):
    guid: str
    environment: str
    created_by_id: str
    created_at: str
    updated_at: str

    @classmethod
    def _from_engine_format(cls, data: dict) -> "Version":
        obj = cls._create_instance(
            **data,
        )
        return obj

    def _to_engine_format(self) -> dict:
        base_dict = asdict(self)
        return {
            **base_dict,
        }


@dataclass
class PromptResponse(BaseDataClass):
    """
    This class represents the Response data model returned from the Klu engine in response to action prompting.
    """

    msg: str
    streaming: bool
    data_guid: Optional[str] = None
    result_url: Optional[str] = None
    feedback_url: Optional[str] = None
    streaming_url: Optional[str] = None

    def __repr__(self):
        return self.generate_repr()


@dataclass
class SyncPromptResponse(BaseDataClass):
    """
    This class represents the Response data model returned
    from the Klu engine in response to non-async, non-streaming action prompting.
    """

    msg: str
    data_guid: Optional[str] = None
    feedback_url: Optional[str] = None

    def __repr__(self):
        return self.generate_repr()


@dataclass
class StreamingPromptResponse(BaseDataClass):
    """
    This class represents the Response data model returned from the Klu engine in response to streaming action prompting.
    """

    msg: str
    streaming_url: Optional[str]
    data_guid: Optional[str] = None

    feedback_url: Optional[str] = None
    sse_client: Optional[Union[SSEClient, OpenAISSEClient]] = None
    payload: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None

    @classmethod
    def _create_instance(cls, **kwargs):
        instance = cls.__new__(cls)
        instance._init_with_base_class(**kwargs)
        return instance

    def _init_with_base_class(self, **kwargs):
        super()._init_with_base_class(**kwargs)
        if self.streaming_url:
            self.sse_client = SSEClient(self.streaming_url)
        elif self.payload:
            self.sse_client = OpenAISSEClient(self.headers, self.payload)

    @property
    def tokens(self) -> Optional[AsyncIterator[str]]:
        if self.sse_client:
            return self.sse_client.get_streaming_data()
        else:
            return None

    def __repr__(self):
        return self.generate_repr()


@dataclass
class AsyncPromptResponse(BaseDataClass):
    """
    This class represents the Response data model returned from the Klu engine in response to async action prompting.
    Contains result_url  - the url that gives access to the result when the prompt is completed or a message about prompting in progress.
    """

    msg: str
    data_guid: Optional[str] = None
    result_url: Optional[str] = None
    feedback_url: Optional[str] = None

    def __repr__(self):
        return self.generate_repr()


@dataclass
class AsyncPromptResultResponse(BaseDataClass):
    """
    This class represents the Response data model returned from the Klu engine in response to triggering result_url
    returned from the async prompting endpoint.
    msg will contain the result once the prompting task is completed.
    """

    msg: str
    status: TaskStatusEnum

    def __repr__(self):
        return self.generate_repr()
