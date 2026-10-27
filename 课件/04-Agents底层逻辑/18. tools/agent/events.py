from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class Event:
    REASONING_START = "reasoning_start"
    REASONING = "reasoning"
    REASONING_END = "reasoning_end"
    CONTENT_START = "content_start"
    CONTENT = "content"
    CONTENT_END = "content_end"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL = "tool_call"
    TOOL_CALL_END = "tool_call_end"
    COMPLETE = "complete"


@dataclass
class EventEmitter:
    _listeners: dict[str, list[Callable[..., Any]]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def on(self, event: str, callback: Callable[..., Any]) -> None:
        self._listeners[event].append(callback)

    def emit(self, event: str, **data: Any) -> None:
        for cb in self._listeners.get(event, []):
            cb(event, **data)
