import json
from pathlib import Path

import yaml
from agent.tool.core import tool

SKILL_BASE_DIR = Path(__file__).parent.parent / ".agents" / "skills"


def parse_skill_file(skill_name: str) -> str:
    skill_file = SKILL_BASE_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"未找到 Skill: {skill_name}")
    return skill_file.read_text(encoding="utf-8")


@tool(skill_name="Skill 的名称")
def use_skill(skill_name: str) -> str:
    """根据 Skill 名称获取其完整描述，返回包含元信息、正文内容和文件路径的 JSON 字符串"""

    markdown_content = parse_skill_file(skill_name)

    parts = markdown_content.split("---")
    meta = {}
    if len(parts) >= 3:
        meta = yaml.safe_load(parts[1])

    skill_file_path = str(SKILL_BASE_DIR / skill_name / "SKILL.md")

    result = {
        "meta": meta,
        "content": markdown_content,
        "path": skill_file_path,
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
