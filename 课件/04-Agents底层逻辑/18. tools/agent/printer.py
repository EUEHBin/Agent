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
            print("思考：")
        elif e == Event.REASONING_END:
            print()
        elif e == Event.CONTENT_START:
            print()
            print("内容：")
        elif e == Event.TOOL_CALL_START:
            print()
            print("工具调用：")
        elif e == Event.TOOL_CALL_END:
            print(json.dumps(args["value"], indent=2, ensure_ascii=False))

        elif e == Event.REASONING:
            print(f"\033[36m{args["chunk_value"]}\033[0m", end="")
        elif e == "content":
            print(f"\033[32m{args["chunk_value"]}\033[0m", end="")
        sys.stdout.flush()
