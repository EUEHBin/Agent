import json
import os
import platform
import subprocess
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

SKILL_BASE_DIR = Path(__file__).parent / ".agents" / "skills"


def list_mcp_info() -> str:
    try:
        from agent.tool.use_mcp import list_mcp_tools

        raw = list_mcp_tools()
        result = []
        for item in raw:
            server_name = item["server"]
            tools = []
            for t in item["tools"].tools:
                tools.append(
                    {
                        "name": t.name,
                        "description": t.description or "",
                        "inputSchema": t.inputSchema,
                    }
                )
            result.append({"server": server_name, "tools": tools})
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        return ""


def get_cwd() -> str:
    return os.getcwd()


def get_os() -> str:
    return platform.system()


def get_is_git() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def list_skills() -> list[dict]:
    if not SKILL_BASE_DIR.exists():
        return []

    skills = []
    for skill_dir in SKILL_BASE_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")
        parts = content.split("---")
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1])
            skills.append({skill_dir.name: meta})

    return skills


def render_prompt(prompt_name: str) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), "prompt")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(f"{prompt_name}.j2")
    return template.render(
        cwd=get_cwd(),
        os=get_os(),
        is_git=get_is_git(),
        skills=list_skills(),
        mcp_servers=list_mcp_info(),
    )
