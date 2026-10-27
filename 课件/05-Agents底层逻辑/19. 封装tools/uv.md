# UV 安装教程

## 什么是 UV？

UV 是一个用 Rust 编写的极速 Python 包管理器和解析器，由 Astral（同样是 Ruff 的开发者）开发。它旨在替代 `pip`、`pip-tools`、`pipx`、`poetry` 等工具，提供更快的依赖解析和安装体验。

## 安装方法

### macOS 和 Linux

使用官方安装脚本：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

或者使用 Homebrew（macOS）：

```bash
brew install uv
```

### Windows

使用 PowerShell 安装：

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

或者使用 Winget：

```bash
winget install --id astral-sh.uv
```

### 使用 pip 安装

```bash
pip install uv
```

### 使用 Cargo 安装（需要 Rust 环境）

```bash
cargo install uv
```

## 验证安装

安装完成后，运行以下命令验证是否安装成功：

```bash
uv --version
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `uv pip install <package>` | 安装包 |
| `uv pip install -r requirements.txt` | 从 requirements 文件安装 |
| `uv venv` | 创建虚拟环境 |
| `uv add <package>` | 将包添加到项目 |
| `uv remove <package>` | 从项目移除包 |
| `uv sync` | 同步项目依赖 |
| `uv run <command>` | 在虚拟环境中运行命令 |
| `uv cache clean` | 清理缓存 |
| `uv tool install <package>` | 安装全局工具（类似 pipx） |

## 更多信息

- 官方文档：https://docs.astral.sh/uv/
- GitHub 仓库：https://github.com/astral-sh/uv
