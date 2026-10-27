from utils.stream_resp import chunk_generator
import sys


def print_stream(stream):
    for chunk in chunk_generator(stream):
        if chunk.type == "reasoning_start":
            print("思考：")
        elif chunk.type == "reasoning_end":
            print()
        elif chunk.type == "content_start":
            print()
            print("内容：")
        elif chunk.type == "content_end":
            print()
            print("====输出完毕====")
        elif chunk.type == "reasoning":
            print(f"\033[36m{chunk.content}\033[0m", end="")
        elif chunk.type == "content":
            print(f"\033[31m{chunk.content}\033[0m", end="")
        sys.stdout.flush()
