import os
import platform
import subprocess

from jinja2 import Environment, FileSystemLoader


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


def render_prompt(prompt_name: str) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), "prompt")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(f"{prompt_name}.j2")
    return template.render(
        cwd=get_cwd(),
        os=get_os(),
        is_git=get_is_git(),
    )
