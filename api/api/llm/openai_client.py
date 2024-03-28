import abc
from api.llm.prompt_builder import Prompt
import openai
from openai import AsyncStream
from openai.types.chat import ChatCompletion
from openai.types.chat import ChatCompletionChunk

from enum import Enum
from typing import AsyncIterator

from api.config import (
    OPENAI_DEFAULT_MAX_TOKENS,
    OPENAI_DEFAULT_TEMPERATURE,
    OPENAI_DEFAULT_TOP_P,
)


class OpenAIModel(str, Enum):
    GPT_3_5_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT_3_5_TURBO_1106 = "gpt-3.5-turbo-1106"
    GPT_3_5_TURBO_0125 = "gpt-3.5-turbo-0125"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"


class OpenAIParams:
    def __init__(
        self,
        *,
        max_tokens: int = OPENAI_DEFAULT_MAX_TOKENS,
        temperature: float = OPENAI_DEFAULT_TEMPERATURE,
        top_p: float = OPENAI_DEFAULT_TOP_P,
        response_format: dict | None = None,
    ):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.response_format = response_format


class OpenAIClientWrapper(abc.ABC):
    @abc.abstractmethod
    async def get_completion_async(
        self, model: OpenAIModel, prompt: Prompt, params: OpenAIParams = OpenAIParams()
    ) -> str:
        pass

    @abc.abstractmethod
    async def stream_completion_async(
        self, model: OpenAIModel, prompt: Prompt, params: OpenAIParams = OpenAIParams()
    ) -> AsyncIterator[str]:
        pass

    @classmethod
    def prompt_to_messages(cls, prompt: Prompt) -> list[dict]:
        return [
            {"role": message.role, "content": message.content}
            for message in prompt.messages
        ]


class DefaultOpenAIClientWrapper(OpenAIClientWrapper):
    def __init__(self, client: openai.AsyncOpenAI):
        self.client = client

    async def get_completion_async(
        self, model: OpenAIModel, prompt: Prompt, params: OpenAIParams = OpenAIParams()
    ) -> str:
        completion: ChatCompletion = await self.client.chat.completions.create(
            max_tokens=params.max_tokens,
            temperature=params.temperature,
            top_p=params.top_p,
            model=model,
            messages=OpenAIClientWrapper.prompt_to_messages(prompt),
            response_format=params.response_format,
        )
        return completion.choices[0].message.content

    async def stream_completion_async(
        self, model: OpenAIModel, prompt: Prompt, params: OpenAIParams = OpenAIParams()
    ) -> AsyncIterator[str]:
        chunks: AsyncStream[
            ChatCompletionChunk
        ] = await self.client.chat.completions.create(
            max_tokens=params.max_tokens,
            temperature=params.temperature,
            top_p=params.top_p,
            model=model,
            messages=OpenAIClientWrapper.prompt_to_messages(prompt),
            stream=True,
            response_format=params.response_format,
        )

        async for chunk in chunks:
            content = chunk.choices[0].delta.content
            if content:
                yield content
