import json
import uuid
from pathlib import Path
from agent.tool import registry
from agent.prompt import render_prompt


class Session:
    def __init__(self, *, system_prompt="", tools=[]):
        self.id = str(uuid.uuid4())
        self.messages: list[dict] = []
        if not system_prompt:
            system_prompt = render_prompt("system")
        self.add_message({"role": "system", "content": render_prompt("system")})
        self.tools = tools or registry.schemas()

    def add_message(self, message: dict):
        self.messages.append(message)

    def __str__(self) -> str:
        data = {"id": self.id, "messages": self.messages, "tools": self.tools}
        return json.dumps(data, ensure_ascii=False, indent=2)

    def print(self):
        print(self)

    def print_friendly(self):
        lines = []
        n = 1

        for msg in self.messages:
            role = msg.get("role")

            if role == "system":
                lines.append(f"====={n}. 系统消息======")
                lines.append(msg.get("content", ""))
                n += 1

            elif role == "user":
                lines.append(f"====={n}. 用户消息======")
                lines.append(msg.get("content", ""))
                n += 1

            elif role == "assistant":
                tool_calls = msg.get("tool_calls")
                if tool_calls:
                    lines.append(f"====={n}. 工具调用======")
                    for i, tc in enumerate(tool_calls):
                        func = tc.get("function", {})
                        name = func.get("name", "未知")
                        lines.append(f"工具名{i + 1}: {name}")

                        args_str = func.get("arguments", "{}")
                        try:
                            args = json.loads(args_str)
                        except json.JSONDecodeError, TypeError:
                            args = {}

                        for k, v in args.items():
                            v_str = str(v)
                            v_str = v_str[:70] if len(v_str) > 70 else v_str
                            lines.append(f"参数{k}: {v_str}")

                        if i < len(tool_calls) - 1:
                            lines.append("")
                    n += 1
                else:
                    lines.append(f"====={n}. AI消息======")
                    lines.append(msg.get("content") or "")
                    n += 1

            elif role == "tool":
                lines.append(f"====={n}. 调用结果======")
                tool_name = msg.get("name", "未知")
                content = msg.get("content") or ""
                lines.append(f"工具名: {tool_name}")
                content_display = content[:50] if len(content) > 50 else content
                lines.append(f"<结果: {content_display}>")
                n += 1

            lines.append("")

        print("\n".join(lines))

    def save(self, prefix=""):
        sessions_dir = Path(__file__).parent / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        data = {"id": self.id, "messages": self.messages, "tools": self.tools}

        path = sessions_dir / f"{prefix}{self.id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, session_id: str):
        path = Path(__file__).parent / "sessions" / f"{session_id}.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        session = cls()
        session.id = data["id"]
        session.messages = data["messages"]
        return session
