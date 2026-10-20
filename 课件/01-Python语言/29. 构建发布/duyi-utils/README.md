# duyi-utils

一个用于学习 Python 公共库构建和发布的示例工程。

## 功能

- **日期工具** — 日期格式化、日期差值计算（依赖 `python-dateutil`）
- **Markdown 工具** — Markdown 转 HTML、去除 Markdown 标记（依赖 `Markdown`）
- **问候工具** — 简单的个性化问候

## 安装

```bash
pip install duyi-utils
```

## 使用

```python
from duyi_utils import format_date, days_until, to_html, strip_markdown
from datetime import date

# 日期工具
format_date(date(2026, 6, 1))    # => "2026年06月01日"
days_until("2026-10-01")          # => 剩余天数

# Markdown 工具
to_html("**Hello**")             # => "<p><strong>Hello</strong></p>"
strip_markdown("**Hello**")      # => "<strong>Hello</strong>"

# 问候工具
from duyi_utils.greeter import greet
greet("小明")                     # => "你好, 小明!"
```
