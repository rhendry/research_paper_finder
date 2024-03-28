from __future__ import annotations

import abc
from enum import Enum
from typing import List
from pydantic import BaseModel


class PromptRole(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class PromptMessage(BaseModel):
    role: PromptRole
    content: str


class Prompt(BaseModel):
    messages: List[PromptMessage]


class PromptBuilderCanBuild(abc.ABC):
    @abc.abstractmethod
    def build(self) -> Prompt:
        pass


class PromptBuilderNeedsUser(PromptBuilderCanBuild):
    @abc.abstractmethod
    def user(self, content: str) -> PromptBuilderNeedsAssistant:
        pass


class PromptBuilderNeedsAssistant(PromptBuilderCanBuild):
    @abc.abstractmethod
    def assistant(self, content: str) -> PromptBuilderNeedsUser:
        pass


class PromptBuilderWithSystem(PromptBuilderCanBuild):
    @abc.abstractmethod
    def user(self, content: str) -> PromptBuilderNeedsAssistant:
        pass

    @abc.abstractmethod
    def assistant(self, content: str) -> PromptBuilderNeedsUser:
        pass


class PromptBuilder(
    PromptBuilderWithSystem, PromptBuilderNeedsUser, PromptBuilderNeedsAssistant
):
    def __init__(self, system: str):
        self.messages: List[PromptMessage] = [
            PromptMessage(role=PromptRole.SYSTEM, content=system)
        ]

    @classmethod
    def system(cls, content: str) -> PromptBuilderWithSystem:
        return PromptBuilder(content)

    def user(self, content: str) -> PromptBuilderNeedsAssistant:
        self.messages.append(PromptMessage(role=PromptRole.USER, content=content))
        return self

    def assistant(self, content: str) -> PromptBuilderNeedsUser:
        self.messages.append(PromptMessage(role=PromptRole.ASSISTANT, content=content))
        return self

    def build(self) -> Prompt:
        return Prompt(messages=self.messages)
