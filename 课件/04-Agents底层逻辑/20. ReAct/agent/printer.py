from dataclasses import dataclass
import json
import sys
from agent.events import Event, EventEmitter
from agent.model import Model


class ModelPrinterListener:

    def __init__(self, model: Model) -> None:
        self.model = model
        self.listening = True
        events = [v for k, v in Event.__dict__.items() if not k.startswith("__")]
        for e in events:
            model.on(event=e, callback=self._model_print_callback)

    def _model_print_callback(self, e: str, **args):
        if not self.listening:
            return
        if e == Event.REASONING_START:
            print("思考中...")
        elif e == Event.REASONING_END:
            print()
        elif e == Event.CONTENT_START:
            print()
            print("内容：")
        elif e == Event.CONTENT_END:
            print()
        elif e == Event.TOOL_CALL_END:
            tool_calls = args["value"]["tool_calls"]
            for call in tool_calls:
                print(f"\033[36m调用工具：{call["function"]["name"]}\033[0m")
        # elif e == Event.REASONING:
        #     print(f"\033[36m{args["chunk_value"]}\033[0m", end="")
        elif e == "content":
            print(f"\033[32m{args["chunk_value"]}\033[0m", end="")
        sys.stdout.flush()
