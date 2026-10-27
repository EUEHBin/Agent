from dataclasses import dataclass
import sys


@dataclass
class PrinterConfig:
    show_reasoning: bool = True
    reasoning_color: str = "36"
    content_color: str = "31"


def print_response(response, config: PrinterConfig | None = None):
    if config is None:
        config = PrinterConfig()
    message = response.choices[0].message
    reasoning_content = getattr(message, "reasoning_content", None)
    if not reasoning_content:
        reasoning_content = getattr(message, "reasoning", None)
    if reasoning_content and config.show_reasoning:
        print(f"\033[{config.reasoning_color}m{reasoning_content}\033[0m")
        print()
    content = message.content
    if content:
        print(f"\033[{config.content_color}m{content}\033[0m")


def print_stream(chunk_iterator, config: PrinterConfig | None = None):
    if config is None:
        config = PrinterConfig()
    for chunk in chunk_iterator:
        if chunk.type == "reasoning_start":
            if config.show_reasoning:
                print("思考：")
        elif chunk.type == "reasoning_end":
            if config.show_reasoning:
                print()
        elif chunk.type == "content_start":
            print()
            print("内容：")
        elif chunk.type == "content_end":
            print()
            print("====输出完毕====")
        elif chunk.type == "reasoning":
            if config.show_reasoning:
                print(f"\033[{config.reasoning_color}m{chunk.content}\033[0m", end="")
        elif chunk.type == "content":
            print(f"\033[{config.content_color}m{chunk.content}\033[0m", end="")
        sys.stdout.flush()
