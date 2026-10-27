import os
import platform
import subprocess

from jinja2 import Environment, FileSystemLoader


def get_cwd() -> str:
    return os.getcwd()


def get_is_git() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def get_language() -> str:
    system = platform.system()
    if system == "Darwin":
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleLocale"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    elif system == "Windows":
        import ctypes

        lcid = ctypes.windll.kernel32.GetUserDefaultLCID()  # type: ignore
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.kernel32.GetLocaleInfoW(lcid, 0x5C, buf, 256)  # type: ignore
        return buf.value
    return ""


def render_prompt(prompt_name: str) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), "prompt")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(f"{prompt_name}.j2")
    return template.render(
        language=get_language(),
        cwd=get_cwd(),
        is_git=get_is_git(),
    )
