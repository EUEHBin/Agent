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

    def save(self):
        sessions_dir = Path(__file__).parent / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "id": self.id,
            "messages": self.messages,
        }

        path = sessions_dir / f"{self.id}.json"
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
