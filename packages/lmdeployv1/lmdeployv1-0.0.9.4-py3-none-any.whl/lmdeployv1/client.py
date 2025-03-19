#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Copyright (c) 2024 Baidu, Inc. 
# All rights reserved.
#
# File    : client
# Author  : zhoubohan
# Date    : 2024/11/29
# Time    : 14:18
# Description :
"""
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Union,
    Callable,
    Any,
    AsyncGenerator,
    Generator,
)

import httpx
from bceidaas.auth.bce_credentials import BceCredentials
from openai import OpenAI, AsyncOpenAI
from openai.pagination import SyncPage
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartParam,
    ChatCompletionContentPartTextParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from openai.types.model import Model
from pyrate_limiter import Limiter, RequestRate
from tenacity import retry, stop_after_attempt

from .api import BatchChatCompletionRequest, BatchChatCompletionResponse, LimiterConfig


class LMDeployError(Exception):
    """Base exception for LMDeploy client."""

    pass


class NoModelsAvailableError(LMDeployError):
    """Raised when no models are available."""

    pass


class APIError(LMDeployError):
    """Raised when API request fails."""

    pass


@contextmanager
def handle_api_errors():
    """Context manager for handling API errors."""
    try:
        yield
    except httpx.HTTPError as e:
        raise APIError(f"API request failed: {str(e)}") from e
    except Exception as e:
        raise LMDeployError(f"Unexpected error: {str(e)}") from e


def build_batch_chat_messages(
    kv_list: List[Dict[str, str]]
) -> List[List[ChatCompletionMessageParam]]:
    """
    Build batch chat messages
    :param kv_list: List{"image_url":"prompt"}
    :return:
    """
    messages: List[List[ChatCompletionMessageParam]] = []

    for kv in kv_list:
        for img_url, prompt in kv.items():
            content: List[ChatCompletionContentPartParam] = []
            text_param = ChatCompletionContentPartTextParam(type="text", text=prompt)
            content.append(text_param)

            image_url = ImageURL(url=img_url)
            image_param = ChatCompletionContentPartImageParam(
                type="image_url", image_url=image_url
            )
            content.append(image_param)

            message_param = ChatCompletionUserMessageParam(role="user", content=content)

            messages.append([message_param])

    return messages


def build_chat_messages(kv: Dict[str, str], is_group_content=False) -> List[ChatCompletionMessageParam]:
    """
    Build chat messages
    :param kv: {"image_url":"prompt"}
    :param is_group_content: bool
    :return:
    """
    messages: List[ChatCompletionMessageParam] = []

    if is_group_content:
        content: List[ChatCompletionContentPartParam] = []
        for img_url, prompt in kv.items():
            text_param = ChatCompletionContentPartTextParam(type="text", text=prompt)
            content.append(text_param)

            image_url = ImageURL(url=img_url)
            image_param = ChatCompletionContentPartImageParam(type="image_url", image_url=image_url)
            content.append(image_param)

            message_param = ChatCompletionUserMessageParam(role="user", content=content)

            messages.append(message_param)

        return messages

    text_content: List[ChatCompletionContentPartParam] = []
    img_content: List[ChatCompletionContentPartParam] = []

    for prompt in kv.values():
        text_param = ChatCompletionContentPartTextParam(type="text", text=prompt)
        text_content.append(text_param)
        messages.append(ChatCompletionUserMessageParam(role="user", content=text_content))

    for img_url in kv.keys():
        image_url = ImageURL(url=img_url)
        image_param = ChatCompletionContentPartImageParam(
            type="image_url", image_url=image_url
        )
        img_content.append(image_param)
        messages.append(ChatCompletionUserMessageParam(role="user", content=img_content))

    return messages


def format_base64_string(s: str) -> str:
    """Format base64 string to proper image format."""
    return f"data:image/jpeg;base64,{s}"


@dataclass
class LMDeployClient:
    """A client for LM deploy service that supports both sync and async operations."""

    endpoint: str
    base_url: str = ""
    credentials: Optional[BceCredentials] = None
    max_retries: int = 1
    timeout_in_seconds: int = 300
    is_async: bool = False
    context: Optional[Dict[str, Any]] = None
    limiter_config: Optional[LimiterConfig] = None

    # Class constants
    DEFAULT_MAX_TOKENS: ClassVar[int] = 512
    DEFAULT_TEMPERATURE: ClassVar[float] = 0.7
    DEFAULT_TOP_P: ClassVar[float] = 1.0
    DEFAULT_PRESENCE_PENALTY: ClassVar[float] = 0.6
    DEFAULT_FREQUENCY_PENALTY: ClassVar[float] = 0.6
    DEFAULT_REPETITION_PENALTY: ClassVar[float] = 1.2

    # Private attributes initialized in post_init
    _identifier: str = field(init=False)
    _openai_client: Union[OpenAI, AsyncOpenAI] = field(init=False)
    _http_client: Union[httpx.Client, httpx.AsyncClient] = field(init=False)
    _limiter: Optional[Limiter] = field(init=False)
    _limiter_delay: Optional[float] = field(init=False)
    _limiter_max_delay: Optional[float] = field(init=False)

    def __post_init__(self):
        """Initialize additional attributes after dataclass initialization."""
        self._identifier = str(uuid.uuid4())
        self._setup_credentials()
        self._setup_endpoint()
        self._setup_limiter()
        self._setup_clients()

    def _setup_credentials(self) -> None:
        """Setup credentials if not provided."""
        if self.credentials is None:
            self.credentials = BceCredentials("", "")

    def _setup_endpoint(self) -> None:
        """Setup API endpoint."""
        if self.base_url == "":
            self.base_url = "v1"
        self.endpoint = f"{self.endpoint.rstrip('/')}/{self.base_url.strip('/')}/"

    def _setup_limiter(self) -> None:
        """Setup rate limiter if config provided."""
        self._limiter = None
        self._limiter_delay = None
        self._limiter_max_delay = None

        if isinstance(self.limiter_config, LimiterConfig):
            self._limiter = Limiter(
                RequestRate(self.limiter_config.limit, self.limiter_config.interval)
            )
            self._limiter_delay = self.limiter_config.delay
            self._limiter_max_delay = self.limiter_config.max_delay

    def _setup_clients(self) -> None:
        """Setup OpenAI and HTTP clients."""
        headers = self._build_headers()

        if self.is_async:
            self._setup_async_clients(headers)
        else:
            self._setup_sync_clients(headers)

    def _build_headers(self) -> Dict[bytes, bytes]:
        """Build request headers from context."""
        headers = {}
        if self.context:
            headers.update(
                {
                    b"x-impersonate-target-org-id": self.context.get(
                        "OrgID", ""
                    ).encode("utf-8"),
                    b"x-impersonate-target-user-id": self.context.get(
                        "UserID", ""
                    ).encode("utf-8"),
                    b"x-impersonate-target-project-id": self.context.get(
                        "ProjectID", ""
                    ).encode("utf-8"),
                }
            )
        return headers

    def _setup_async_clients(self, headers: Dict[bytes, bytes]) -> None:
        """Setup async clients."""
        self._openai_client = AsyncOpenAI(
            api_key=self.credentials.access_key_id,
            base_url=self.endpoint,
            max_retries=self.max_retries,
            timeout=self.timeout_in_seconds,
            default_headers=headers,
        )

        self._http_client = httpx.AsyncClient(
            base_url=self.endpoint,
            timeout=self.timeout_in_seconds,
            headers=headers,
        )

    def _setup_sync_clients(self, headers: Dict[bytes, bytes]) -> None:
        """Setup sync clients."""
        self._openai_client = OpenAI(
            api_key=self.credentials.access_key_id,
            base_url=self.endpoint,
            max_retries=self.max_retries,
            timeout=self.timeout_in_seconds,
            default_headers=headers,
        )

        self._http_client = httpx.Client(
            base_url=self.endpoint,
            timeout=self.timeout_in_seconds,
            headers=headers,
        )

    def _create_completion_params(self, **kwargs) -> Dict[str, Any]:
        """Create standardized completion parameters."""
        return {
            "messages": kwargs["messages"],
            "model": kwargs.get("model", ""),
            "n": kwargs.get("n", 1),
            "max_completion_tokens": kwargs.get(
                "max_completion_tokens", self.DEFAULT_MAX_TOKENS
            ),
            "max_tokens": kwargs.get("max_tokens", self.DEFAULT_MAX_TOKENS),
            "temperature": kwargs.get("temperature", self.DEFAULT_TEMPERATURE),
            "top_p": kwargs.get("top_p", self.DEFAULT_TOP_P),
            "presence_penalty": kwargs.get(
                "presence_penalty", self.DEFAULT_PRESENCE_PENALTY
            ),
            "frequency_penalty": kwargs.get(
                "frequency_penalty", self.DEFAULT_FREQUENCY_PENALTY
            ),
            "stream": kwargs.get("stream", False),
            "extra_body": {
                "repetition_penalty": kwargs.get(
                    "repetition_penalty", self.DEFAULT_REPETITION_PENALTY
                )
            },
        }

    async def _execute_with_rate_limit(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with rate limiting if configured."""
        if self._limiter is not None:
            async with self._limiter.ratelimit(
                self._identifier,
                delay=self._limiter_delay,
                max_delay=self._limiter_max_delay,
            ):
                return await func(*args, **kwargs)
        return await func(*args, **kwargs)

    @lru_cache(maxsize=128)
    async def async_models(self) -> SyncPage[Model]:
        """Get available models with caching."""
        return await self._openai_client.models.list()

    def models(self) -> SyncPage[Model]:
        """Get available models."""
        return self._openai_client.models.list()

    async def async_available_models(self) -> str:
        """Get first available model asynchronously."""
        models = await self.async_models()
        if not models.data:
            raise NoModelsAvailableError("No available models")
        return models.data[0].id

    def available_models(self) -> str:
        """Get first available model synchronously."""
        models = self.models()
        if not models.data:
            raise NoModelsAvailableError("No available models")
        return models.data[0].id

    async def chat_acompletion(
        self, messages: List[ChatCompletionMessageParam], **kwargs
    ) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
        """Async chat completion."""
        params = self._create_completion_params(messages=messages, **kwargs)
        return await self._execute_with_rate_limit(
            self._openai_client.chat.completions.create, **params
        )

    def chat_completion(
        self, messages: List[ChatCompletionMessageParam], **kwargs
    ) -> Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]]:
        """Sync chat completion."""
        params = self._create_completion_params(messages=messages, **kwargs)

        if self._limiter is not None:
            with self._limiter.ratelimit(
                self._identifier,
                delay=self._limiter_delay,
                max_delay=self._limiter_max_delay,
            ):
                return self._openai_client.chat.completions.create(**params)
        return self._openai_client.chat.completions.create(**params)

    @retry(stop=stop_after_attempt(max_retries), reraise=True)
    async def batch_chat_acompletion(
        self,
        request: BatchChatCompletionRequest,
    ) -> BatchChatCompletionResponse:
        """Async batch chat completion with retry."""
        with handle_api_errors():
            response = await self._execute_with_rate_limit(
                self._http_client.post,
                url="chat/batch_completions",
                json=request.model_dump(),
            )
            await response.aclose()
            response.raise_for_status()
            return BatchChatCompletionResponse.model_validate(response.json())

    @retry(stop=stop_after_attempt(max_retries), reraise=True)
    def batch_chat_completion(
        self,
        request: BatchChatCompletionRequest,
    ) -> BatchChatCompletionResponse:
        """Sync batch chat completion with retry."""
        with handle_api_errors():
            if self._limiter is not None:
                with self._limiter.ratelimit(
                    self._identifier,
                    delay=self._limiter_delay,
                    max_delay=self._limiter_max_delay,
                ):
                    return self._execute_batch_request(request)
            return self._execute_batch_request(request)

    def _execute_batch_request(
        self, request: BatchChatCompletionRequest
    ) -> BatchChatCompletionResponse:
        """Execute batch request."""
        response = self._http_client.post(
            url="chat/batch_completions", json=request.model_dump(mode="json")
        )
        response.close()
        response.raise_for_status()
        return BatchChatCompletionResponse.model_validate(response.json())
