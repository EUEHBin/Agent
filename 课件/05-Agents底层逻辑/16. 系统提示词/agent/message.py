from abc import ABC
from dataclasses import dataclass
from typing import Literal

Role = Literal["system", "user", "assistant"]


@dataclass
class Message(ABC):
    content: str  # 先放无默认值的
    role: Role  # 后放有默认值的


@dataclass
class SystemMessage(Message):
    role: Role = "system"


@dataclass
class UserMessage(Message):
    role: Role = "user"


@dataclass
class AssistantMessage(Message):
    role: Role = "assistant"
