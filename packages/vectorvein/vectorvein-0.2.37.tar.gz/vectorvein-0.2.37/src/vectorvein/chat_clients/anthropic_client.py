# @Author: Bi Ying
# @Date:   2024-07-26 14:48:55
import json
from typing import (
    Any,
    Dict,
    List,
    TYPE_CHECKING,
    overload,
    Generator,
    AsyncGenerator,
    Union,
    Literal,
    Iterable,
    Optional,
)

import httpx
from openai._types import NotGiven as OpenAINotGiven
from openai._types import NOT_GIVEN as OPENAI_NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types.shared_params.metadata import Metadata
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat.chat_completion_modality import ChatCompletionModality
from openai.types.chat.chat_completion_audio_param import ChatCompletionAudioParam
from openai.types.chat.chat_completion_reasoning_effort import ChatCompletionReasoningEffort
from openai.types.chat.chat_completion_stream_options_param import ChatCompletionStreamOptionsParam
from openai.types.chat.chat_completion_prediction_content_param import ChatCompletionPredictionContentParam
from anthropic import (
    Anthropic,
    AnthropicVertex,
    AsyncAnthropic,
    AsyncAnthropicVertex,
    AnthropicBedrock,
    AsyncAnthropicBedrock,
)
from anthropic._types import NOT_GIVEN
from anthropic._exceptions import APIStatusError as AnthropicAPIStatusError
from anthropic._exceptions import APIConnectionError as AnthropicAPIConnectionError
from anthropic.types import (
    TextBlock,
    ThinkingBlock,
    RedactedThinkingBlock,
    MessageParam,
    ToolUseBlock,
    ThinkingConfigParam,
    RawMessageDeltaEvent,
    RawMessageStartEvent,
    RawContentBlockStartEvent,
    RawContentBlockDeltaEvent,
)

from ..types import defaults as defs
from .utils import cutoff_messages, get_message_token_counts
from .base_client import BaseChatClient, BaseAsyncChatClient
from .openai_compatible_client import OpenAICompatibleChatClient, AsyncOpenAICompatibleChatClient
from ..types.exception import APIStatusError, APIConnectionError
from ..types.enums import ContextLengthControlType, BackendType
from ..types.llm_parameters import (
    Usage,
    NotGiven,
    ToolParam,
    ToolChoice,
    AnthropicToolParam,
    AnthropicToolChoice,
    ChatCompletionMessage,
    ChatCompletionToolParam,
    ChatCompletionDeltaMessage,
)

if TYPE_CHECKING:
    from ..settings import Settings
    from ..types.settings import SettingsDict


def refactor_tool_use_params(tools: Iterable[ChatCompletionToolParam]) -> list[AnthropicToolParam]:
    return [
        {
            "name": tool["function"]["name"],
            "description": tool["function"].get("description", ""),
            "input_schema": tool["function"].get("parameters", {}),
        }
        for tool in tools
    ]


def refactor_tool_calls(tool_calls: list):
    return [
        {
            "index": index,
            "id": tool["id"],
            "type": "function",
            "function": {
                "name": tool["name"],
                "arguments": json.dumps(tool["input"], ensure_ascii=False),
            },
        }
        for index, tool in enumerate(tool_calls)
    ]


def refactor_tool_choice(tool_choice: ToolChoice) -> AnthropicToolChoice:
    if isinstance(tool_choice, str):
        if tool_choice == "auto":
            return {"type": "auto"}
        elif tool_choice == "required":
            return {"type": "any"}
    elif isinstance(tool_choice, dict) and "function" in tool_choice:
        return {"type": "tool", "name": tool_choice["function"]["name"]}
    return {"type": "auto"}


def format_messages_alternate(messages: list) -> list:
    # messages: roles must alternate between "user" and "assistant", and not multiple "user" roles in a row
    # reformat multiple "user" roles in a row into {"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}, {"type": "text", "text": "How are you?"}]}
    # same for assistant role
    # if not multiple "user" or "assistant" roles in a row, keep it as is

    formatted_messages = []
    current_role = None
    current_content = []

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role != current_role:
            if current_content:
                formatted_messages.append({"role": current_role, "content": current_content})
                current_content = []
            current_role = role

        if isinstance(content, str):
            current_content.append({"type": "text", "text": content})
        elif isinstance(content, list):
            current_content.extend(content)
        else:
            current_content.append(content)

    if current_content:
        formatted_messages.append({"role": current_role, "content": current_content})

    return formatted_messages


def refactor_into_openai_messages(messages: Iterable[MessageParam]):
    formatted_messages = []
    for message in messages:
        content = message["content"]
        if isinstance(content, str):
            formatted_messages.append(message)
        elif isinstance(content, list):
            _content = []
            for item in content:
                if isinstance(item, (TextBlock, ToolUseBlock)):
                    _content.append(item.model_dump())
                elif isinstance(item, (ThinkingBlock, RedactedThinkingBlock)):
                    continue
                elif item.get("type") == "image":
                    image_data = item.get("source", {}).get("data", "")
                    media_type = item.get("source", {}).get("media_type", "")
                    data_url = f"data:{media_type};base64,{image_data}"
                    _content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url,
                                "detail_type": "auto",
                            },
                        }
                    )
                else:
                    _content.append(item)
            formatted_messages.append({"role": message["role"], "content": _content})
        else:
            formatted_messages.append(message)
    return formatted_messages


class AnthropicChatClient(BaseChatClient):
    DEFAULT_MODEL: str = defs.ANTHROPIC_DEFAULT_MODEL
    BACKEND_NAME: BackendType = BackendType.Anthropic

    def __init__(
        self,
        model: str = defs.ANTHROPIC_DEFAULT_MODEL,
        stream: bool = True,
        temperature: float | None | NotGiven = NOT_GIVEN,
        context_length_control: ContextLengthControlType = defs.CONTEXT_LENGTH_CONTROL,
        random_endpoint: bool = True,
        endpoint_id: str = "",
        http_client: httpx.Client | None = None,
        backend_name: str | None = None,
        settings: "Settings | SettingsDict | None" = None,  # Use default settings if not provided
    ):
        super().__init__(
            model,
            stream,
            temperature,
            context_length_control,
            random_endpoint,
            endpoint_id,
            http_client,
            backend_name,
            settings,
        )
        self.model_id = None
        self.endpoint = None

    @property
    def raw_client(self):  # type: ignore
        self.endpoint, self.model_id = self._set_endpoint()

        if self.endpoint.proxy is not None and self.http_client is None:
            self.http_client = httpx.Client(proxy=self.endpoint.proxy)

        if self.endpoint.is_vertex or self.endpoint.endpoint_type == "anthropic_vertex":
            if self.endpoint.credentials is None:
                raise ValueError("Anthropic Vertex endpoint requires credentials")

            from google.auth import _helpers
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            self.creds = Credentials(
                token=self.endpoint.credentials.get("token"),
                refresh_token=self.endpoint.credentials.get("refresh_token"),
                token_uri=self.endpoint.credentials.get("token_uri"),
                scopes=None,
                client_id=self.endpoint.credentials.get("client_id"),
                client_secret=self.endpoint.credentials.get("client_secret"),
                quota_project_id=self.endpoint.credentials.get("quota_project_id"),
                expiry=_helpers.utcnow() - _helpers.REFRESH_THRESHOLD,
                rapt_token=self.endpoint.credentials.get("rapt_token"),
                trust_boundary=self.endpoint.credentials.get("trust_boundary"),
                universe_domain=self.endpoint.credentials.get("universe_domain", "googleapis.com"),
                account=self.endpoint.credentials.get("account", ""),
            )

            if self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())

            if self.endpoint.api_base is None:
                base_url = None
            else:
                base_url = f"{self.endpoint.api_base}{self.endpoint.region}-aiplatform/v1"

            region = NOT_GIVEN if self.endpoint.region is None else self.endpoint.region
            return AnthropicVertex(
                region=region,
                base_url=base_url,
                project_id=self.endpoint.credentials.get("quota_project_id", NOT_GIVEN),
                access_token=self.creds.token,
                http_client=self.http_client,
            )
        elif self.endpoint.is_bedrock or self.endpoint.endpoint_type == "anthropic_bedrock":
            if self.endpoint.credentials is None:
                raise ValueError("Anthropic Bedrock endpoint requires credentials")
            return AnthropicBedrock(
                aws_access_key=self.endpoint.credentials.get("access_key"),
                aws_secret_key=self.endpoint.credentials.get("secret_key"),
                aws_region=self.endpoint.region,
                base_url=self.endpoint.api_base,
                http_client=self.http_client,
            )
        elif self.endpoint.api_schema_type == "default":
            return Anthropic(
                api_key=self.endpoint.api_key,
                base_url=self.endpoint.api_base,
                http_client=self.http_client,
            )
        elif self.endpoint.api_schema_type == "openai":
            return OpenAICompatibleChatClient(
                model=self.model,
                stream=self.stream,
                temperature=self.temperature,
                context_length_control=self.context_length_control,
                random_endpoint=self.random_endpoint,
                endpoint_id=self.endpoint_id,
                http_client=self.http_client,
                backend_name=self.BACKEND_NAME,
            ).raw_client

    @overload
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = OPENAI_NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        user: str | OpenAINotGiven = OPENAI_NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = OPENAI_NOT_GIVEN,
    ) -> ChatCompletionMessage:
        pass

    @overload
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[True],
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = OPENAI_NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        user: str | OpenAINotGiven = OPENAI_NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = OPENAI_NOT_GIVEN,
    ) -> Generator[ChatCompletionDeltaMessage, None, None]:
        pass

    @overload
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: bool,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = OPENAI_NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        user: str | OpenAINotGiven = OPENAI_NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = OPENAI_NOT_GIVEN,
    ) -> ChatCompletionMessage | Generator[ChatCompletionDeltaMessage, Any, None]:
        pass

    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] | Literal[True] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = OPENAI_NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        user: str | OpenAINotGiven = OPENAI_NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = OPENAI_NOT_GIVEN,
    ):
        if model is not None:
            self.model = model
        if stream is not None:
            self.stream = stream
        if temperature is not None:
            self.temperature = temperature

        self.model_setting = self.backend_settings.models[self.model]
        if self.model_id is None:
            self.model_id = self.model_setting.id

        self.endpoint, self.model_id = self._set_endpoint()

        if self.endpoint.api_schema_type == "openai":
            _tools = OPENAI_NOT_GIVEN if tools is NOT_GIVEN else tools
            _tool_choice = OPENAI_NOT_GIVEN if tool_choice is NOT_GIVEN else tool_choice

            formatted_messages = refactor_into_openai_messages(messages)

            if self.stream:

                def _generator():
                    response = OpenAICompatibleChatClient(
                        model=self.model,
                        stream=True,
                        temperature=self.temperature,
                        context_length_control=self.context_length_control,
                        random_endpoint=self.random_endpoint,
                        endpoint_id=self.endpoint_id,
                        http_client=self.http_client,
                        backend_name=self.BACKEND_NAME,
                    ).create_completion(
                        messages=formatted_messages,
                        model=model,
                        stream=True,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        tools=_tools,
                        tool_choice=_tool_choice,
                        response_format=response_format,
                        stream_options=stream_options,
                        top_p=top_p,
                        skip_cutoff=skip_cutoff,
                        audio=audio,
                        frequency_penalty=frequency_penalty,
                        logit_bias=logit_bias,
                        logprobs=logprobs,
                        max_completion_tokens=max_completion_tokens,
                        metadata=metadata,
                        modalities=modalities,
                        n=n,
                        parallel_tool_calls=parallel_tool_calls,
                        prediction=prediction,
                        presence_penalty=presence_penalty,
                        reasoning_effort=reasoning_effort,
                        seed=seed,
                        service_tier=service_tier,
                        stop=stop,
                        store=store,
                        top_logprobs=top_logprobs,
                        user=user,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout,
                    )
                    for chunk in response:
                        yield chunk

                return _generator()
            else:
                return OpenAICompatibleChatClient(
                    model=self.model,
                    stream=False,
                    temperature=self.temperature,
                    context_length_control=self.context_length_control,
                    random_endpoint=self.random_endpoint,
                    endpoint_id=self.endpoint_id,
                    http_client=self.http_client,
                    backend_name=self.BACKEND_NAME,
                ).create_completion(
                    messages=formatted_messages,
                    model=model,
                    stream=False,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=_tools,
                    tool_choice=_tool_choice,
                    response_format=response_format,
                    top_p=top_p,
                    skip_cutoff=skip_cutoff,
                    audio=audio,
                    frequency_penalty=frequency_penalty,
                    logit_bias=logit_bias,
                    logprobs=logprobs,
                    max_completion_tokens=max_completion_tokens,
                    metadata=metadata,
                    modalities=modalities,
                    n=n,
                    parallel_tool_calls=parallel_tool_calls,
                    prediction=prediction,
                    presence_penalty=presence_penalty,
                    reasoning_effort=reasoning_effort,
                    seed=seed,
                    service_tier=service_tier,
                    stop=stop,
                    store=store,
                    top_logprobs=top_logprobs,
                    user=user,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                )

        raw_client = self.raw_client  # 调用完 self.raw_client 后，self.model_id 会被赋值
        assert isinstance(raw_client, Anthropic | AnthropicVertex | AnthropicBedrock)

        if isinstance(tools, OpenAINotGiven):
            tools = NOT_GIVEN
        if isinstance(tool_choice, OpenAINotGiven):
            tool_choice = NOT_GIVEN
        if isinstance(top_p, OpenAINotGiven) or top_p is None:
            top_p = NOT_GIVEN
        if isinstance(self.temperature, NotGiven) or self.temperature is None:
            self.temperature = NOT_GIVEN
        if isinstance(thinking, NotGiven) or thinking is None:
            thinking = NOT_GIVEN

        if messages[0].get("role") == "system":
            system_prompt: str = messages[0]["content"]
            messages = messages[1:]
        else:
            system_prompt = ""

        if not skip_cutoff and self.context_length_control == ContextLengthControlType.Latest:
            messages = cutoff_messages(
                messages,
                max_count=self.model_setting.context_length,
                backend=self.BACKEND_NAME,
                model=self.model,
            )

        messages = format_messages_alternate(messages)

        tools_params: list[AnthropicToolParam] | NotGiven = refactor_tool_use_params(tools) if tools else NOT_GIVEN
        tool_choice_param = NOT_GIVEN
        if tool_choice:
            tool_choice_param = refactor_tool_choice(tool_choice)

        if max_tokens is None:
            max_output_tokens = self.model_setting.max_output_tokens
            token_counts = get_message_token_counts(messages=messages, tools=tools_params, model=self.model)
            if max_output_tokens is not None:
                max_tokens = self.model_setting.context_length - token_counts
                max_tokens = min(max(max_tokens, 1), max_output_tokens)
            else:
                max_tokens = self.model_setting.context_length - token_counts

        self._acquire_rate_limit(self.endpoint, self.model, messages)

        if self.stream:
            try:
                stream_response = raw_client.messages.create(
                    model=self.model_id,
                    messages=messages,
                    system=system_prompt,
                    stream=True,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    tools=tools_params,
                    tool_choice=tool_choice_param,
                    top_p=top_p,
                    thinking=thinking,
                )
            except AnthropicAPIStatusError as e:
                raise APIStatusError(message=e.message, response=e.response, body=e.body)
            except AnthropicAPIConnectionError as e:
                raise APIConnectionError(message=e.message, request=e.request)

            def generator():
                result = {"content": "", "reasoning_content": "", "usage": {}, "tool_calls": []}
                for chunk in stream_response:
                    message = {"content": "", "tool_calls": []}
                    if isinstance(chunk, RawMessageStartEvent):
                        result["usage"] = {"prompt_tokens": chunk.message.usage.input_tokens}
                        continue
                    elif isinstance(chunk, RawContentBlockStartEvent):
                        if chunk.content_block.type == "tool_use":
                            result["tool_calls"] = message["tool_calls"] = [
                                {
                                    "index": 0,
                                    "id": chunk.content_block.id,
                                    "function": {
                                        "arguments": "",
                                        "name": chunk.content_block.name,
                                    },
                                    "type": "function",
                                }
                            ]
                        elif chunk.content_block.type == "text":
                            message["content"] = chunk.content_block.text
                        elif chunk.content_block.type == "thinking":
                            message["reasoning_content"] = chunk.content_block.thinking
                        yield ChatCompletionDeltaMessage(**message)
                    elif isinstance(chunk, RawContentBlockDeltaEvent):
                        if chunk.delta.type == "text_delta":
                            message["content"] = chunk.delta.text
                            result["content"] += chunk.delta.text
                        elif chunk.delta.type == "thinking_delta":
                            message["reasoning_content"] = chunk.delta.thinking
                            result["reasoning_content"] += chunk.delta.thinking
                        elif chunk.delta.type == "input_json_delta":
                            result["tool_calls"][0]["function"]["arguments"] += chunk.delta.partial_json
                            message["tool_calls"] = [
                                {
                                    "index": 0,
                                    "id": result["tool_calls"][0]["id"],
                                    "function": {
                                        "arguments": chunk.delta.partial_json,
                                        "name": result["tool_calls"][0]["function"]["name"],
                                    },
                                    "type": "function",
                                }
                            ]
                        yield ChatCompletionDeltaMessage(**message)
                    elif isinstance(chunk, RawMessageDeltaEvent):
                        result["usage"]["completion_tokens"] = chunk.usage.output_tokens
                        result["usage"]["total_tokens"] = (
                            result["usage"]["prompt_tokens"] + result["usage"]["completion_tokens"]
                        )
                        yield ChatCompletionDeltaMessage(
                            usage=Usage(
                                prompt_tokens=result["usage"]["prompt_tokens"],
                                completion_tokens=result["usage"]["completion_tokens"],
                                total_tokens=result["usage"]["total_tokens"],
                            )
                        )

            return generator()
        else:
            try:
                response = raw_client.messages.create(
                    model=self.model_id,
                    messages=messages,
                    system=system_prompt,
                    stream=False,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    tools=tools_params,
                    tool_choice=tool_choice_param,
                    top_p=top_p,
                    thinking=thinking,
                )
            except AnthropicAPIStatusError as e:
                raise APIStatusError(message=e.message, response=e.response, body=e.body)
            except AnthropicAPIConnectionError as e:
                raise APIConnectionError(message=e.message, request=e.request)

            result = {
                "content": "",
                "reasoning_content": "",
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            }
            tool_calls = []
            for content_block in response.content:
                if isinstance(content_block, TextBlock):
                    result["content"] += content_block.text
                elif isinstance(content_block, ThinkingBlock):
                    result["reasoning_content"] = content_block.thinking
                elif isinstance(content_block, ToolUseBlock):
                    tool_calls.append(content_block.model_dump())

            if tool_calls:
                result["tool_calls"] = refactor_tool_calls(tool_calls)

            return ChatCompletionMessage(**result)


class AsyncAnthropicChatClient(BaseAsyncChatClient):
    DEFAULT_MODEL: str = defs.ANTHROPIC_DEFAULT_MODEL
    BACKEND_NAME: BackendType = BackendType.Anthropic

    def __init__(
        self,
        model: str = defs.ANTHROPIC_DEFAULT_MODEL,
        stream: bool = True,
        temperature: float | None | NotGiven = NOT_GIVEN,
        context_length_control: ContextLengthControlType = defs.CONTEXT_LENGTH_CONTROL,
        random_endpoint: bool = True,
        endpoint_id: str = "",
        http_client: httpx.AsyncClient | None = None,
        backend_name: str | None = None,
        settings: "Settings | SettingsDict | None" = None,  # Use default settings if not provided
    ):
        super().__init__(
            model,
            stream,
            temperature,
            context_length_control,
            random_endpoint,
            endpoint_id,
            http_client,
            backend_name,
            settings,
        )
        self.model_id = None
        self.endpoint = None

    @property
    def raw_client(self):  # type: ignore
        self.endpoint, self.model_id = self._set_endpoint()

        if self.endpoint.proxy is not None and self.http_client is None:
            self.http_client = httpx.AsyncClient(proxy=self.endpoint.proxy)

        if self.endpoint.is_vertex or self.endpoint.endpoint_type == "anthropic_vertex":
            if self.endpoint.credentials is None:
                raise ValueError("Anthropic Vertex endpoint requires credentials")

            from google.auth import _helpers
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            self.creds = Credentials(
                token=self.endpoint.credentials.get("token"),
                refresh_token=self.endpoint.credentials.get("refresh_token"),
                token_uri=self.endpoint.credentials.get("token_uri"),
                scopes=None,
                client_id=self.endpoint.credentials.get("client_id"),
                client_secret=self.endpoint.credentials.get("client_secret"),
                quota_project_id=self.endpoint.credentials.get("quota_project_id"),
                expiry=_helpers.utcnow() - _helpers.REFRESH_THRESHOLD,
                rapt_token=self.endpoint.credentials.get("rapt_token"),
                trust_boundary=self.endpoint.credentials.get("trust_boundary"),
                universe_domain=self.endpoint.credentials.get("universe_domain", "googleapis.com"),
                account=self.endpoint.credentials.get("account", ""),
            )

            if self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())

            if self.endpoint.api_base is None:
                base_url = None
            else:
                base_url = f"{self.endpoint.api_base}{self.endpoint.region}-aiplatform/v1"

            region = NOT_GIVEN if self.endpoint.region is None else self.endpoint.region
            return AsyncAnthropicVertex(
                region=region,
                base_url=base_url,
                project_id=self.endpoint.credentials.get("quota_project_id", NOT_GIVEN),
                access_token=self.creds.token,
                http_client=self.http_client,
            )
        elif self.endpoint.is_bedrock or self.endpoint.endpoint_type == "anthropic_bedrock":
            if self.endpoint.credentials is None:
                raise ValueError("Anthropic Bedrock endpoint requires credentials")
            return AsyncAnthropicBedrock(
                aws_access_key=self.endpoint.credentials.get("access_key"),
                aws_secret_key=self.endpoint.credentials.get("secret_key"),
                aws_region=self.endpoint.region,
                http_client=self.http_client,
            )
        elif self.endpoint.api_schema_type == "default":
            return AsyncAnthropic(
                api_key=self.endpoint.api_key,
                base_url=self.endpoint.api_base,
                http_client=self.http_client,
            )
        elif self.endpoint.api_schema_type == "openai":
            return AsyncOpenAICompatibleChatClient(
                model=self.model,
                stream=self.stream,
                temperature=self.temperature,
                context_length_control=self.context_length_control,
                random_endpoint=self.random_endpoint,
                endpoint_id=self.endpoint_id,
                http_client=self.http_client,
                backend_name=self.BACKEND_NAME,
            ).raw_client

    @overload
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = OPENAI_NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        user: str | OpenAINotGiven = OPENAI_NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = OPENAI_NOT_GIVEN,
    ) -> ChatCompletionMessage:
        pass

    @overload
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[True],
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = OPENAI_NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        user: str | OpenAINotGiven = OPENAI_NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = OPENAI_NOT_GIVEN,
    ) -> AsyncGenerator[ChatCompletionDeltaMessage, Any]:
        pass

    @overload
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: bool,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = OPENAI_NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        user: str | OpenAINotGiven = OPENAI_NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = OPENAI_NOT_GIVEN,
    ) -> ChatCompletionMessage | AsyncGenerator[ChatCompletionDeltaMessage, Any]:
        pass

    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] | Literal[True] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None = None,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None = None,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = OPENAI_NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = OPENAI_NOT_GIVEN,
        user: str | OpenAINotGiven = OPENAI_NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = OPENAI_NOT_GIVEN,
    ):
        if model is not None:
            self.model = model
        if stream is not None:
            self.stream = stream
        if temperature is not None:
            self.temperature = temperature

        self.model_setting = self.backend_settings.models[self.model]
        if self.model_id is None:
            self.model_id = self.model_setting.id

        self.endpoint, self.model_id = self._set_endpoint()

        if self.endpoint.api_schema_type == "openai":
            _tools = OPENAI_NOT_GIVEN if tools is NOT_GIVEN else tools
            _tool_choice = OPENAI_NOT_GIVEN if tool_choice is NOT_GIVEN else tool_choice

            formatted_messages = refactor_into_openai_messages(messages)

            if self.stream:

                async def _generator():
                    client = AsyncOpenAICompatibleChatClient(
                        model=self.model,
                        stream=True,
                        temperature=self.temperature,
                        context_length_control=self.context_length_control,
                        random_endpoint=self.random_endpoint,
                        endpoint_id=self.endpoint_id,
                        http_client=self.http_client,
                        backend_name=self.BACKEND_NAME,
                    )
                    response = await client.create_completion(
                        messages=formatted_messages,
                        model=model,
                        stream=True,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        tools=_tools,
                        tool_choice=_tool_choice,
                        response_format=response_format,
                        stream_options=stream_options,
                        top_p=top_p,
                        skip_cutoff=skip_cutoff,
                        audio=audio,
                        frequency_penalty=frequency_penalty,
                        logit_bias=logit_bias,
                        logprobs=logprobs,
                        max_completion_tokens=max_completion_tokens,
                        metadata=metadata,
                        modalities=modalities,
                        n=n,
                        parallel_tool_calls=parallel_tool_calls,
                        prediction=prediction,
                        presence_penalty=presence_penalty,
                        reasoning_effort=reasoning_effort,
                        seed=seed,
                        service_tier=service_tier,
                        stop=stop,
                        store=store,
                        top_logprobs=top_logprobs,
                        user=user,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout,
                    )
                    async for chunk in response:
                        yield chunk

                return _generator()
            else:
                client = AsyncOpenAICompatibleChatClient(
                    model=self.model,
                    stream=False,
                    temperature=self.temperature,
                    context_length_control=self.context_length_control,
                    random_endpoint=self.random_endpoint,
                    endpoint_id=self.endpoint_id,
                    http_client=self.http_client,
                    backend_name=self.BACKEND_NAME,
                )
                return await client.create_completion(
                    messages=formatted_messages,
                    model=model,
                    stream=False,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=_tools,
                    tool_choice=_tool_choice,
                    response_format=response_format,
                    top_p=top_p,
                    skip_cutoff=skip_cutoff,
                    audio=audio,
                    frequency_penalty=frequency_penalty,
                    logit_bias=logit_bias,
                    logprobs=logprobs,
                    max_completion_tokens=max_completion_tokens,
                    metadata=metadata,
                    modalities=modalities,
                    n=n,
                    parallel_tool_calls=parallel_tool_calls,
                    prediction=prediction,
                    presence_penalty=presence_penalty,
                    reasoning_effort=reasoning_effort,
                    seed=seed,
                    service_tier=service_tier,
                    stop=stop,
                    store=store,
                    top_logprobs=top_logprobs,
                    user=user,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                )

        raw_client = self.raw_client  # 调用完 self.raw_client 后，self.model_id 会被赋值
        assert isinstance(raw_client, AsyncAnthropic | AsyncAnthropicVertex | AsyncAnthropicBedrock)

        if isinstance(tools, OpenAINotGiven):
            tools = NOT_GIVEN
        if isinstance(tool_choice, OpenAINotGiven):
            tool_choice = NOT_GIVEN
        if isinstance(top_p, OpenAINotGiven) or top_p is None:
            top_p = NOT_GIVEN
        if isinstance(self.temperature, NotGiven) or self.temperature is None:
            self.temperature = NOT_GIVEN
        if isinstance(thinking, NotGiven) or thinking is None:
            thinking = NOT_GIVEN

        if messages[0].get("role") == "system":
            system_prompt = messages[0]["content"]
            messages = messages[1:]
        else:
            system_prompt = ""

        if not skip_cutoff and self.context_length_control == ContextLengthControlType.Latest:
            messages = cutoff_messages(
                messages,
                max_count=self.model_setting.context_length,
                backend=self.BACKEND_NAME,
                model=self.model,
            )

        messages = format_messages_alternate(messages)

        tools_params: list[AnthropicToolParam] | NotGiven = refactor_tool_use_params(tools) if tools else NOT_GIVEN
        tool_choice_param = NOT_GIVEN
        if tool_choice:
            tool_choice_param = refactor_tool_choice(tool_choice)

        if max_tokens is None:
            max_output_tokens = self.model_setting.max_output_tokens
            token_counts = get_message_token_counts(messages=messages, tools=tools_params, model=self.model)
            if max_output_tokens is not None:
                max_tokens = self.model_setting.context_length - token_counts
                max_tokens = min(max(max_tokens, 1), max_output_tokens)
            else:
                max_tokens = self.model_setting.context_length - token_counts

        await self._acquire_rate_limit(self.endpoint, self.model, messages)

        if self.stream:
            try:
                stream_response = await raw_client.messages.create(
                    model=self.model_id,
                    messages=messages,
                    system=system_prompt,
                    stream=True,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    tools=tools_params,
                    tool_choice=tool_choice_param,
                    top_p=top_p,
                    thinking=thinking,
                )
            except AnthropicAPIStatusError as e:
                raise APIStatusError(message=e.message, response=e.response, body=e.body)
            except AnthropicAPIConnectionError as e:
                raise APIConnectionError(message=e.message, request=e.request)

            async def generator():
                result = {"content": "", "reasoning_content": "", "usage": {}, "tool_calls": []}
                async for chunk in stream_response:
                    message = {"content": "", "tool_calls": []}
                    if isinstance(chunk, RawMessageStartEvent):
                        result["usage"] = {"prompt_tokens": chunk.message.usage.input_tokens}
                        continue
                    elif isinstance(chunk, RawContentBlockStartEvent):
                        if chunk.content_block.type == "tool_use":
                            result["tool_calls"] = message["tool_calls"] = [
                                {
                                    "index": 0,
                                    "id": chunk.content_block.id,
                                    "function": {
                                        "arguments": "",
                                        "name": chunk.content_block.name,
                                    },
                                    "type": "function",
                                }
                            ]
                        elif chunk.content_block.type == "text":
                            message["content"] = chunk.content_block.text
                        elif chunk.content_block.type == "thinking":
                            message["reasoning_content"] = chunk.content_block.thinking
                        yield ChatCompletionDeltaMessage(**message)
                    elif isinstance(chunk, RawContentBlockDeltaEvent):
                        if chunk.delta.type == "text_delta":
                            message["content"] = chunk.delta.text
                            result["content"] += chunk.delta.text
                        elif chunk.delta.type == "thinking_delta":
                            message["reasoning_content"] = chunk.delta.thinking
                            result["reasoning_content"] += chunk.delta.thinking
                        elif chunk.delta.type == "input_json_delta":
                            result["tool_calls"][0]["function"]["arguments"] += chunk.delta.partial_json
                            message["tool_calls"] = [
                                {
                                    "index": 0,
                                    "id": result["tool_calls"][0]["id"],
                                    "function": {
                                        "arguments": chunk.delta.partial_json,
                                        "name": result["tool_calls"][0]["function"]["name"],
                                    },
                                    "type": "function",
                                }
                            ]
                        yield ChatCompletionDeltaMessage(**message)
                    elif isinstance(chunk, RawMessageDeltaEvent):
                        result["usage"]["completion_tokens"] = chunk.usage.output_tokens
                        result["usage"]["total_tokens"] = (
                            result["usage"]["prompt_tokens"] + result["usage"]["completion_tokens"]
                        )
                        yield ChatCompletionDeltaMessage(
                            usage=Usage(
                                prompt_tokens=result["usage"]["prompt_tokens"],
                                completion_tokens=result["usage"]["completion_tokens"],
                                total_tokens=result["usage"]["total_tokens"],
                            )
                        )

            return generator()
        else:
            try:
                response = await raw_client.messages.create(
                    model=self.model_id,
                    messages=messages,
                    system=system_prompt,
                    stream=False,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    tools=tools_params,
                    tool_choice=tool_choice_param,
                    top_p=top_p,
                    thinking=thinking,
                )
            except AnthropicAPIStatusError as e:
                raise APIStatusError(message=e.message, response=e.response, body=e.body)
            except AnthropicAPIConnectionError as e:
                raise APIConnectionError(message=e.message, request=e.request)

            result = {
                "content": "",
                "reasoning_content": "",
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            }
            tool_calls = []
            for content_block in response.content:
                if isinstance(content_block, TextBlock):
                    result["content"] += content_block.text
                elif isinstance(content_block, ThinkingBlock):
                    result["reasoning_content"] = content_block.thinking
                elif isinstance(content_block, ToolUseBlock):
                    tool_calls.append(content_block.model_dump())

            if tool_calls:
                result["tool_calls"] = refactor_tool_calls(tool_calls)

            return ChatCompletionMessage(**result)
