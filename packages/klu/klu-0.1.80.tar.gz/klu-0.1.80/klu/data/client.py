# mypy: disable-error-code="override"
from typing import Any, Dict, Optional

from klu.common.client import KluClientBase
from klu.data.constants import DATA_ENDPOINT
from klu.data.models import Data, DataSourceType
from klu.utils.dict_helpers import dict_no_empty


class DataClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, DATA_ENDPOINT, Data)

    async def create(
        self,
        input: str,
        output: str,
        action_guid: str,
        full_prompt_sent: Optional[str] = None,
        meta_data: Optional[dict] = None,
        session_guid: Optional[str] = None,
        model: Optional[str] = None,
        model_provider: Optional[str] = None,
        system_message: Optional[str] = None,
        latency: Optional[int] = None,
        num_output_tokens: Optional[int] = None,
        num_input_tokens: Optional[int] = None,
    ) -> Data:
        """
        Creates a new data instance for the provided action_guid.

        Args:
            input (str): Input value of the action execution. This will usually be a JSON dumped dictionary of the variables and the values.
            output (str): The result of the action execution.
            action_guid (str): The guid of the action the data belongs to.
            full_prompt_sent (str, optional): The full prompt that was sent to the LLM. Can take in both an array of messages and a string.
            meta_data (dict, optional): Data meta_data.
            session_guid (str, optional): The guid of the session the data belongs to.
            model (str, optional): The model used for the action execution.
            model_provider (str, optional): The provider of the model.
            system_message (str, optional): A system message related to the data.
            latency (int, optional): The latency of the action execution.
            num_output_tokens (int, optional): The number of output tokens.
            num_input_tokens (int, optional): The number of input tokens.

        Returns:
            The created Data object.
        """
        meta_data = meta_data or {}
        return await super().create(
            input=input,
            output=output,
            action=action_guid,
            session=session_guid,
            full_prompt_sent=full_prompt_sent,
            model=model,
            model_provider=model_provider,
            system_message=system_message,
            latency=latency,
            num_output_tokens=num_output_tokens,
            num_input_tokens=num_input_tokens,
            meta_data={
                **meta_data,
                "source": meta_data.pop("source", DataSourceType.SDK),
            },
        )

    async def get(self, guid: str) -> Data:
        """
        Retrieves data information based on the data guid.

        Args:
            guid (str): guid of a data object to fetch.

        Returns:
            A Data object
        """
        return await super().get(guid)

    async def update(
        self,
        guid: str,
        meta_data: Optional[Dict] = None,
        full_prompt_sent: Optional[str] = None,
        num_output_tokens: Optional[int] = None,
        num_input_tokens: Optional[int] = None,
        latency: Optional[int] = None,
        output: Optional[str] = None,
        raw_llm_response: Optional[Any] = None,
        system_message: Optional[str] = None,
        model_provider: Optional[str] = None,
        model: Optional[str] = None,
        input: Optional[str] = None,
        prompt_template: Optional[str] = None,
        app: Optional[str] = None,
        session: Optional[str] = None,
        action: Optional[str] = None,
    ) -> Data:
        """
        Updated data information based on the data ID and provided payload. Currently, only supports `output` update.

        Args:

        Returns:
            Newly updated Data object
        """
        data = {
            "meta_data": meta_data,
            "full_prompt_sent": full_prompt_sent,
            "num_output_tokens": num_output_tokens,
            "num_input_tokens": num_input_tokens,
            "latency": latency,
            "output": output,
            "raw_llm_response": raw_llm_response,
            "system_message": system_message,
            "model_provider": model_provider,
            "model": model,
            "input": input,
            "prompt_template": prompt_template,
            "app": app,
            "session": session,
            "action": action,
        }
        return await super().update(**{"guid": guid, **dict_no_empty(data)})

    async def delete(self, guid: str) -> Data:
        return await super().delete(guid)
