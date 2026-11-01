import asyncio
import base64
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from deepagents.backends.protocol import (
    DeleteResult,
    EditResult,
    ExecuteResponse,
    FileDownloadResponse,
    FileInfo,
    FileUploadResponse,
    GlobResult,
    GrepMatch,
    GrepResult,
    LsResult,
    ReadResult,
    SandboxBackendProtocol,
    WriteResult,
)
from deepagents.backends.utils import (
    compile_grep_include_glob,
    compile_recursive_glob,
    perform_string_replacement,
    slice_read_response,
)
from e2b import AsyncSandbox
from e2b.exceptions import FileNotFoundException
from e2b.sandbox.filesystem.filesystem import EntryInfo, FileType
from langgraph.config import get_config
from langgraph.runtime import get_runtime

from langchain_python.core.sandbox import TIMEOUT, get_sandbox

WORKSPACE_DIR = "/home/user/workspace"


def _entry_to_file_info(entry: EntryInfo) -> FileInfo:
    return {
        "path": entry.path,
        "is_dir": entry.type == FileType.DIR,
        "size": entry.size,
        "modified_at": entry.modified_time.isoformat(),
    }


class AliyunSandboxBackend(SandboxBackendProtocol):
    """Async-only Deep Agents backend backed by the project's Aliyun sandbox."""

    @property
    def id(self) -> str:
        thread_id = get_config().get("configurable", {}).get("thread_id")
        if thread_id is None:
            msg = "AliyunSandboxBackend requires configurable.thread_id"
            raise RuntimeError(msg)
        return str(thread_id)

    async def _get_sandbox(self) -> AsyncSandbox:
        store = get_runtime().store
        if store is None:
            msg = "AliyunSandboxBackend requires a runtime store"
            raise RuntimeError(msg)
        return await get_sandbox(key=self.id, store=store)

    @asynccontextmanager
    async def _sandbox_operation(self) -> AsyncIterator[AsyncSandbox]:
        sandbox = await self._get_sandbox()
        await sandbox.set_timeout(TIMEOUT)
        try:
            yield sandbox
        finally:
            await sandbox.set_timeout(TIMEOUT)

    async def aexecute(
        self,
        command: str,
        *,
        timeout: int | None = 60,
    ) -> ExecuteResponse:
        try:
            async with self._sandbox_operation() as sandbox:
                result = await sandbox.commands.run(
                    command,
                    cwd=WORKSPACE_DIR,
                    timeout=timeout if timeout is not None else 60,
                )
            return ExecuteResponse(
                output=result.stdout + result.stderr,
                exit_code=result.exit_code,
            )
        except Exception as exc:
            return ExecuteResponse(
                output=f"Error executing command: {exc}",
                exit_code=1,
            )

    async def als(self, path: str) -> LsResult:
        try:
            async with self._sandbox_operation() as sandbox:
                entries = await sandbox.files.list(path, depth=1)
            return LsResult(entries=[_entry_to_file_info(entry) for entry in entries])
        except Exception as exc:
            return LsResult(error=f"Error listing directory {path!r}: {exc}")

    async def aread(
        self,
        file_path: str,
        offset: int = 0,
        limit: int = 2000,
    ) -> ReadResult:
        try:
            async with self._sandbox_operation() as sandbox:
                content = bytes(
                    await sandbox.files.read(
                        file_path,
                        format="bytes",
                    )
                )
        except Exception as exc:
            return ReadResult(error=f"Error reading file {file_path!r}: {exc}")

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            return ReadResult(
                file_data={
                    "content": base64.b64encode(content).decode("ascii"),
                    "encoding": "base64",
                }
            )

        return slice_read_response(
            {"content": text, "encoding": "utf-8"},
            offset,
            limit,
        )

    async def agrep(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
        *,
        max_count: int | None = None,
    ) -> GrepResult:
        search_path = path or "/"
        try:
            include = compile_grep_include_glob(glob) if glob else None
            async with self._sandbox_operation() as sandbox:
                entries = await sandbox.files.list(search_path, depth=None)

                matches: list[GrepMatch] = []
                for entry in entries:
                    if entry.type != FileType.FILE:
                        continue

                    relative_path = entry.path.removeprefix(
                        search_path.rstrip("/") + "/"
                    ).lstrip("/")
                    if include is not None and not include(relative_path):
                        continue

                    try:
                        content = await sandbox.files.read(entry.path, format="text")
                    except Exception:
                        continue

                    for line_number, line in enumerate(content.splitlines(), start=1):
                        if pattern not in line:
                            continue
                        if max_count is not None and len(matches) >= max(max_count, 0):
                            return GrepResult(matches=matches, truncated=True)
                        matches.append(
                            {
                                "path": entry.path,
                                "line": line_number,
                                "text": line,
                            }
                        )
        except Exception as exc:
            return GrepResult(error=f"Error searching path {search_path!r}: {exc}")

        return GrepResult(matches=matches)

    async def aglob(self, pattern: str, path: str | None = None) -> GlobResult:
        search_path = path or "/"
        try:
            matcher = compile_recursive_glob(pattern)
            async with self._sandbox_operation() as sandbox:
                entries = await sandbox.files.list(search_path, depth=None)
        except Exception as exc:
            return GlobResult(error=f"Error globbing path {search_path!r}: {exc}")

        matches: list[FileInfo] = []
        for entry in entries:
            if entry.type != FileType.FILE:
                continue
            relative_path = entry.path.removeprefix(
                search_path.rstrip("/") + "/"
            ).lstrip("/")
            if matcher(relative_path):
                matches.append(_entry_to_file_info(entry))
        return GlobResult(matches=matches)

    async def awrite(self, file_path: str, content: str) -> WriteResult:
        try:
            async with self._sandbox_operation() as sandbox:
                await sandbox.files.write(file_path, content)
            return WriteResult(path=file_path)
        except Exception as exc:
            return WriteResult(error=f"Error writing file {file_path!r}: {exc}")

    async def aedit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> EditResult:
        try:
            async with self._sandbox_operation() as sandbox:
                content = await sandbox.files.read(file_path, format="text")
                replacement = perform_string_replacement(
                    content,
                    old_string,
                    new_string,
                    replace_all,
                )
                if isinstance(replacement, str):
                    return EditResult(error=replacement)

                new_content, occurrences = replacement
                await sandbox.files.write(file_path, new_content)
            return EditResult(path=file_path, occurrences=occurrences)
        except Exception as exc:
            return EditResult(error=f"Error editing file {file_path!r}: {exc}")

    async def aupload_files(
        self,
        files: list[tuple[str, bytes]],
    ) -> list[FileUploadResponse]:
        async with self._sandbox_operation() as sandbox:
            async def upload(file_path: str, content: bytes) -> FileUploadResponse:
                try:
                    await sandbox.files.write(file_path, content)
                    return FileUploadResponse(path=file_path)
                except Exception as exc:
                    return FileUploadResponse(path=file_path, error=str(exc))

            return list(
                await asyncio.gather(
                    *(upload(file_path, content) for file_path, content in files)
                )
            )

    async def adownload_files(
        self,
        paths: list[str],
    ) -> list[FileDownloadResponse]:
        async with self._sandbox_operation() as sandbox:
            async def download(file_path: str) -> FileDownloadResponse:
                try:
                    content = bytes(
                        await sandbox.files.read(
                            file_path,
                            format="bytes",
                        )
                    )
                    return FileDownloadResponse(path=file_path, content=content)
                except FileNotFoundException:
                    return FileDownloadResponse(path=file_path, error="file_not_found")
                except Exception as exc:
                    return FileDownloadResponse(path=file_path, error=str(exc))

            return list(await asyncio.gather(*(download(path) for path in paths)))

    async def adelete(self, file_path: str) -> DeleteResult:
        try:
            async with self._sandbox_operation() as sandbox:
                if not await sandbox.files.exists(file_path):
                    return DeleteResult(error=f"Error: File {file_path!r} not found")
                await sandbox.files.remove(file_path)
            return DeleteResult(path=file_path)
        except Exception as exc:
            return DeleteResult(error=f"Error deleting {file_path!r}: {exc}")
