#!/usr/bin/env python3
"""查找 git 仓库中变更的测试文件，并逐个串行运行。"""

import subprocess
import sys
import tomllib
from pathlib import Path


def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(result.stdout.strip())


def get_changed_files(repo_root: Path) -> set[Path]:
    changed: set[Path] = set()

    commands = [
        ["git", "diff", "--name-only", "--cached", "HEAD"],
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]

    for cmd in commands:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=repo_root,
        )
        for line in result.stdout.strip().splitlines():
            if line:
                changed.add(repo_root / line)

    return changed


def load_test_dirs(repo_root: Path) -> list[Path]:
    config_path = repo_root / "pyproject.toml"
    if not config_path.exists():
        print("pyproject.toml 不存在")
        return []

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    patterns: list[str] = config.get("tool", {}).get("test-runner", {}).get("test_dirs", [])
    if not patterns:
        print("[tool.test-runner] 中未配置 test_dirs")
        return []

    dirs: list[Path] = []
    for pattern in patterns:
        for p in repo_root.glob(pattern):
            if p.is_dir():
                dirs.append(p)

    return dirs


def _is_test_module(file: Path) -> bool:
    if file.suffix != ".py":
        return False
    name = file.stem
    if name in ("__init__", "conftest"):
        return False
    return name.startswith("test_") or name.endswith("_test")


def find_test_files(changed_files: set[Path], test_dirs: list[Path]) -> list[Path]:
    test_files: list[Path] = []
    for f in sorted(changed_files):
        if not _is_test_module(f):
            continue
        for test_dir in test_dirs:
            try:
                f.relative_to(test_dir)
                test_files.append(f)
                break
            except ValueError:
                continue
    return test_files


def run_test(test_file: Path, repo_root: Path) -> bool:
    rel_path = test_file.relative_to(repo_root)
    print(f"\n{'=' * 60}")
    print(f"运行: {rel_path}")
    print(f"{'=' * 60}")

    result = subprocess.run(
        ["uv", "run", "pytest", str(test_file), "-q"],
        cwd=repo_root,
    )
    return result.returncode == 0


def main() -> None:
    repo_root = get_repo_root()
    changed_files = get_changed_files(repo_root)

    if not changed_files:
        print("没有变更的文件。")
        return

    test_dirs = load_test_dirs(repo_root)
    if not test_dirs:
        sys.exit(1)

    test_files = find_test_files(changed_files, test_dirs)
    if not test_files:
        print("变更文件中没有测试脚本。")
        return

    print(f"发现 {len(test_files)} 个变更的测试文件:")
    for f in test_files:
        print(f"  {f.relative_to(repo_root)}")

    failed: list[Path] = []
    passed = 0
    for test_file in test_files:
        if run_test(test_file, repo_root):
            passed += 1
        else:
            failed.append(test_file)

    print(f"\n{'=' * 60}")
    print(f"结果: {passed} 通过, {len(failed)} 失败")
    if failed:
        print("失败的测试:")
        for f in failed:
            print(f"  {f.relative_to(repo_root)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
