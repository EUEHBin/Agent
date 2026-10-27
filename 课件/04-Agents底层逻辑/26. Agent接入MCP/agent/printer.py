import json
import sys
from agent.events import Event, EventEmitter
from agent.listener import ModelListener


class ModelPrinterListener(ModelListener):

    def _handler(self, e: str, **args):
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
        elif e == "content":
            print(f"\033[32m{args["chunk_value"]}\033[0m", end="")
        sys.stdout.flush()
