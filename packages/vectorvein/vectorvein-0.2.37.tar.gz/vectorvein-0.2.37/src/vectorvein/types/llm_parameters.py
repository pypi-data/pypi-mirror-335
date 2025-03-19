# @Author: Bi Ying
# @Date:   2024-07-26 23:48:04
from typing import List, Dict, Optional, Union, Iterable, Literal

import httpx
from pydantic import BaseModel, Field

from anthropic._types import NotGiven as AnthropicNotGiven
from anthropic._types import NOT_GIVEN as ANTHROPIC_NOT_GIVEN
from anthropic.types import ToolParam as AnthropicToolParam
from anthropic.types import ThinkingConfigParam, ThinkingConfigEnabledParam
from anthropic.types.message_create_params import ToolChoice as AnthropicToolChoice

from openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI
from openai._types import NotGiven as OpenAINotGiven
from openai._types import NOT_GIVEN as OPENAI_NOT_GIVEN
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.completion_usage import CompletionTokensDetails, PromptTokensDetails
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_stream_options_param import ChatCompletionStreamOptionsParam
from openai.types.chat.chat_completion_tool_choice_option_param import ChatCompletionToolChoiceOptionParam

from . import defaults as defs
from .settings import EndpointOptionDict


class EndpointSetting(BaseModel):
    id: str = Field(..., description="The id of the endpoint.")
    region: Optional[str] = Field(None, description="The region for the endpoint.")
    api_base: Optional[str] = Field(None, description="The base URL for the API.")
    api_key: Optional[str] = Field(None, description="The API key for authentication.")
    endpoint_type: Optional[
        Literal[
            "default",
            "openai",
            "openai_azure",
            "anthropic",
            "anthropic_vertex",
            "anthropic_bedrock",
        ]
    ] = Field(
        "default",
        description="The type of endpoint. Set to 'default' will determine the type automatically.",
    )
    api_schema_type: Optional[Literal["default", "openai", "anthropic"]] = Field(
        "default",
        description="The type of client for the endpoint. Set to 'default' will determine the type automatically.",
    )
    credentials: Optional[dict] = Field(None, description="Additional credentials if needed.")
    is_azure: bool = Field(False, description="Indicates if the endpoint is for Azure.")
    is_vertex: bool = Field(False, description="Indicates if the endpoint is for Vertex.")
    is_bedrock: bool = Field(False, description="Indicates if the endpoint is for Bedrock.")
    rpm: int = Field(description="Requests per minute.", default=defs.ENDPOINT_RPM)
    tpm: int = Field(description="Tokens per minute.", default=defs.ENDPOINT_TPM)
    concurrent_requests: int = Field(
        description="Whether to use concurrent requests for the LLM service.",
        default=defs.ENDPOINT_CONCURRENT_REQUESTS,
    )
    proxy: Optional[str] = Field(None, description="The proxy URL for the endpoint.")

    def model_list(self):
        http_client = httpx.Client(proxy=self.proxy) if self.proxy is not None else None

        if self.is_azure:
            if self.api_base is None:
                raise ValueError("Azure endpoint is not set")
            _client = AzureOpenAI(
                azure_endpoint=self.api_base,
                api_key=self.api_key,
                api_version="2025-01-01-preview",
                http_client=http_client,
            )
        else:
            _client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                http_client=http_client,
            )

        return _client.models.list().model_dump()

    async def amodel_list(self):
        http_client = httpx.AsyncClient(proxy=self.proxy) if self.proxy is not None else None

        if self.is_azure:
            if self.api_base is None:
                raise ValueError("Azure endpoint is not set")
            _client = AsyncAzureOpenAI(
                azure_endpoint=self.api_base,
                api_key=self.api_key,
                api_version="2025-01-01-preview",
                http_client=http_client,
            )
        else:
            _client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                http_client=http_client,
            )

        return (await _client.models.list()).model_dump()


class ModelSetting(BaseModel):
    id: str = Field(..., description="The id of the model.")
    endpoints: List[Union[str, EndpointOptionDict]] = Field(
        default_factory=list, description="Available endpoints for the model."
    )
    function_call_available: bool = Field(False, description="Indicates if function call is available.")
    response_format_available: bool = Field(False, description="Indicates if response format is available.")
    native_multimodal: bool = Field(False, description="Indicates if the model is a native multimodal model.")
    context_length: int = Field(32768, description="The context length for the model.")
    max_output_tokens: Optional[int] = Field(None, description="Maximum number of output tokens allowed.")


class BackendSettings(BaseModel):
    models: Dict[str, ModelSetting] = Field(default_factory=dict)

    def update_models(self, default_models: Dict[str, Dict], input_models: Dict[str, Dict]):
        updated_models = {}
        for model_name, model_data in default_models.items():
            updated_model = ModelSetting(**model_data)
            if model_name in input_models:
                updated_model = updated_model.model_copy(update=input_models[model_name])
            updated_models[model_name] = updated_model

        # Add any new models from input that weren't in defaults
        for model_name, model_data in input_models.items():
            if model_name not in updated_models:
                updated_models[model_name] = ModelSetting(**model_data)

        self.models = updated_models


class Usage(BaseModel):
    completion_tokens: int

    prompt_tokens: int

    total_tokens: int

    completion_tokens_details: Optional[CompletionTokensDetails] = None
    """Breakdown of tokens used in a completion."""

    prompt_tokens_details: Optional[PromptTokensDetails] = None
    """Breakdown of tokens used in the prompt."""


class ChatCompletionMessage(BaseModel):
    content: Optional[str] = None

    reasoning_content: Optional[str] = None

    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None
    """The tool calls generated by the model, such as function calls."""

    function_call_arguments: Optional[dict] = None

    usage: Optional[Usage] = None


class ChatCompletionDeltaMessage(BaseModel):
    content: Optional[str] = None

    reasoning_content: Optional[str] = None

    tool_calls: Optional[List[ChoiceDeltaToolCall]] = None
    """The tool calls generated by the model, such as function calls."""

    function_call_arguments: Optional[dict] = None

    usage: Optional[Usage] = None


NotGiven = Union[AnthropicNotGiven, OpenAINotGiven]

NOT_GIVEN = OPENAI_NOT_GIVEN

OpenAIToolParam = ChatCompletionToolParam
ToolParam = OpenAIToolParam

Tools = Iterable[ToolParam]

ToolChoice = ChatCompletionToolChoiceOptionParam


__all__ = [
    "EndpointSetting",
    "ModelSetting",
    "BackendSettings",
    "Usage",
    "ChatCompletionMessage",
    "ChatCompletionDeltaMessage",
    "ChatCompletionStreamOptionsParam",
    "NotGiven",
    "NOT_GIVEN",
    "OpenAIToolParam",
    "ToolParam",
    "Tools",
    "ToolChoice",
    "AnthropicToolParam",
    "AnthropicToolChoice",
    "OPENAI_NOT_GIVEN",
    "ANTHROPIC_NOT_GIVEN",
    "ResponseFormat",
    "ThinkingConfigParam",
    "ThinkingConfigEnabledParam",
]
