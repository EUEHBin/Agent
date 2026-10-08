from ai_tools import completions


def chat() -> None:
    messages: list[dict[str, str]] = []

    print("AI 聊天工具 (输入 /exit 退出)")
    print("=" * 40)

    while True:
        user_input: str = input("\n你: ").strip()
        if user_input == "/exit":
            print("再见！")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        stream = completions(messages)
        print("AI: ", end="", flush=True)
        full_content = ""
        for content in stream:
            print(content, end="", flush=True)
            full_content += content
        messages.append({"role": "assistant", "content": full_content})
        print()


if __name__ == "__main__":
    chat()
