import posixpath
import shlex
from urllib.parse import quote

from langchain.tools import tool
from langchain_core.tools import ToolException
from langgraph.config import get_config
from langgraph.runtime import get_runtime
from pydantic import BaseModel, Field, field_validator

from langchain_python.core.sandbox import get_sandbox

OUTPUT_DIR = "/home/user/output"
PUBLIC_BASE_URL = "http://duyi-course.yuanjin.tech"


class DeployInput(BaseModel):
    path: str = Field(
        description="沙箱内的产物路径，它可以是文件夹，也可以是文件。\n"
        "这些路径表示要最终交付给用户的产物。\n"
        "比如："
        '"/home/user/workspace/my-vue-app/dist"\n'
        '"/home/user/workspace/my-vue-app/assets/charts.png"\n'
        '"/home/user/workspace/my-vue-app/other.tar.gz"\n'
        "如果指定的是目录，该工具会自动递归读取该目录下的所有文件进行部署"
    )
    target_dirname: str = Field(
        description="部署的目标目录名称。\n"
        "该工具会把path指定的产物放到云存储的某个存储路径中。\n"
        "存储路径是： <前缀>/<target_dirname>/。"
        "前缀是什么你无需关心，你只需要指定target_dirname即可。\n"
        "建议该值直接取用workspace中的工程名字"
    )
    entry_files: list[str] = Field(
        min_length=1,
        description="指定部署完成过后，要访问的入口文件名称。\n"
        '比如：["index.html"、"chart.png"]',
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, path: str) -> str:
        path = posixpath.normpath(path.strip())
        if not path.startswith("/"):
            raise ValueError("path必须是沙箱内的绝对路径")
        if path == OUTPUT_DIR or path.startswith(f"{OUTPUT_DIR}/"):
            raise ValueError("path不能位于部署输出目录中")
        return path

    @field_validator("target_dirname")
    @classmethod
    def validate_target_dirname(cls, target_dirname: str) -> str:
        target_dirname = target_dirname.strip()
        if (
            not target_dirname
            or target_dirname in {".", ".."}
            or "/" in target_dirname
            or "\\" in target_dirname
        ):
            raise ValueError("target_dirname必须是单个安全的目录名")
        return target_dirname

    @field_validator("entry_files")
    @classmethod
    def validate_entry_files(cls, entry_files: list[str]) -> list[str]:
        normalized: list[str] = []
        for entry_file in entry_files:
            entry_file = entry_file.strip()
            normalized_entry = posixpath.normpath(entry_file)
            if (
                not entry_file
                or normalized_entry in {".", ".."}
                or normalized_entry.startswith("../")
                or normalized_entry.startswith("/")
                or "\\" in normalized_entry
            ):
                raise ValueError("entry_files只能包含目标目录内的相对路径")
            normalized.append(normalized_entry)

        if len(normalized) != len(set(normalized)):
            raise ValueError("entry_files不能重复")
        return normalized


def _public_url(thread_id: str, target_dirname: str, entry_file: str) -> str:
    encoded_entry = "/".join(quote(part, safe="") for part in entry_file.split("/"))
    return (
        f"{PUBLIC_BASE_URL}/{quote(thread_id, safe='')}/output/"
        f"{quote(target_dirname, safe='')}/{encoded_entry}"
    )


@tool(args_schema=DeployInput)
async def deploy(
    path: str,
    target_dirname: str,
    entry_files: list[str],
) -> list[str]:
    """
    把沙箱内的文件或目录部署到云存储，并返回入口文件的访问地址。

    调用示例：
    deploy(
        path="/home/user/workspace/my-vue-app/dist",
        target_dirname="my-vue-app",
        entry_files=["index.html"]
    )

    返回示例：
    [
        "https://deploy.com/a2e9d7d8/output/my-vue-app/index.html"
    ]
    """
    thread_id = get_config().get("configurable", {}).get("thread_id")
    if thread_id is None:
        raise RuntimeError("部署工具需要configurable.thread_id")

    store = get_runtime().store
    if store is None:
        raise RuntimeError("部署工具需要runtime store")

    sandbox = await get_sandbox(key=str(thread_id), store=store)
    if not await sandbox.files.exists(path):
        raise ToolException(f"待部署的产物不存在，请检查path后重试: {path}")

    destination = posixpath.join(OUTPUT_DIR, target_dirname)
    temporary_destination = f"{destination}.deploying"
    quoted_path = shlex.quote(path)
    quoted_destination = shlex.quote(destination)
    quoted_temporary = shlex.quote(temporary_destination)
    command = (
        "set -eu\n"
        f"rm -rf -- {quoted_temporary}\n"
        f"mkdir -p -- {quoted_temporary}\n"
        f"if [ -d {quoted_path} ]; then\n"
        f"  cp -R -- {quoted_path}/. {quoted_temporary}/\n"
        "else\n"
        f"  cp -- {quoted_path} {quoted_temporary}/\n"
        "fi\n"
        f"rm -rf -- {quoted_destination}\n"
        f"mv -- {quoted_temporary} {quoted_destination}"
    )
    result = await sandbox.commands.run(command, timeout=300)
    if result.exit_code != 0:
        detail = (result.stderr or result.stdout).strip()
        raise ToolException(
            f"部署产物失败，请检查产物路径和内容后重试: {detail or '未知错误'}"
        )

    missing_entries = [
        entry_file
        for entry_file in entry_files
        if not await sandbox.files.exists(posixpath.join(destination, entry_file))
    ]
    if missing_entries:
        raise ToolException(
            "部署后找不到入口文件，请修正entry_files后重试: "
            + ", ".join(missing_entries)
        )

    public_urls = [
        _public_url(str(thread_id), target_dirname, entry_file)
        for entry_file in entry_files
    ]
    await sandbox.kill()
    return public_urls


deploy.handle_tool_error = True
