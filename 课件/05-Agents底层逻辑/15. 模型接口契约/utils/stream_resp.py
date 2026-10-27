from dataclasses import dataclass


@dataclass
class Chunk:
    type: str = ""
    content: str = ""


def chunk_generator(stream):
    is_on_reasoning = False
    for chunk in stream:
        if len(chunk.choices) == 0:
            continue
        delta = chunk.choices[0].delta
        content = delta.content  # 正文内容
        # 推理内容，为了兼容性，尝试获取两个字段的值。
        reasoning_content = getattr(delta, "reasoning_content", None)
        if not reasoning_content:
            reasoning_content = getattr(delta, "reasoning", None)

        if reasoning_content:
            if not is_on_reasoning:
                is_on_reasoning = True
                yield Chunk(type="reasoning_start")  # 推理开始
            # 推理内容
            yield Chunk(type="reasoning", content=reasoning_content)
        if content:
            if is_on_reasoning:
                is_on_reasoning = False
                # 推理结束
                yield Chunk(type="reasoning_end")
                # 正文开始
                yield Chunk(type="content_start")
            # 正文内容
            yield Chunk(type="content", content=content)

    yield Chunk(type="content_end")
