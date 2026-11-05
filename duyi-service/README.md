# duyi-service（完整工程）

课件里每一节的 `duyi-service` 大多是**增量切片**（只给本课改动的文件），需要拷进你自己的工程。  
本目录由课件第 10～20 讲切片合并而成，是当前唯一完整的本地工程。

## 合并来源

| 顺序 | 课件 | 带入内容 |
|------|------|----------|
| 底座 | 10 中间件 | products/categories/skus、中间件、基础 migrations、cors |
| + | 12 测试方案 | unit/integration/e2e 测试骨架 |
| + | 14 文件上传 | `packages/duyi-utils` 上传能力 |
| + | 15 系统设置 | setting 模型/API/service（切片为扁平目录，已归位到 `app/`） |
| + | 16 长短事务 | upload API、短事务 `get_db`、upload-demo |
| + | 17 用户系统 | JWT/用户、Makefile、login-demo、user 迁移 |
| + | 18 日志 | loguru、request_id 中间件 |
| + | 19 AI 导购 | AiService、AIChat、会话表迁移、AI 设置项 |
| + | 20 流式响应 | SSE/WS 路由、`demo/ai-demo`、最终 `main.py` |

另补：`801112c7f902_add_settings.py`（课件未收录；`add_user` 的 `down_revision` 指向它）。

## 迁移链

```text
ee949af06bdb (init)
  → 1651f4cfdc3e (delete sku stock)
  → dcaa229114a8 (sku add stock)
  → 801112c7f902 (add settings)   ← 本工程补齐
  → 680245532545 (add user)
  → 5406e945234c (ai conversation)
```

## 快速启动

```bash
cd duyi-service

# 1. 依赖（务必 --all-packages，否则只装根目录开发依赖）
# 若官方源很慢，可先：export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
uv sync --all-packages

# 2. 确认 .env（已从 .env.example 复制一份，按本机 Postgres 改）
# DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD
# WEB_JWT_SECRET_KEY

# 3. 先建好空库 duyi_db，再升级表结构到最新
make db-upgrade

# 4. 启动 API（默认 8080）
make dev
```

浏览器打开文档：`http://127.0.0.1:8080/docs`

### AI 导购前端

```bash
cd demo/ai-demo
pnpm install   # 或 npm install
pnpm dev       # 默认 3000，/api 代理到 8080
```

使用前在系统设置里配好 `ai_api_key` / `ai_base_url` / `ai_model`（服务启动时会初始化设置项）。

## 目录要点

```text
apps/web-service/app/main.py     后端入口（含 ai / ai_sse / ai_ws）
apps/web-service/app/service/ai_service.py
packages/duyi-utils/.../ai/chat.py
demo/ai-demo/                    流式聊天演示
demo/login-demo/                 登录/设置演示
demo/upload-demo/                上传演示
```

## 说明

- 合并时后课覆盖前课同名文件；`cors.py` 在 18/20 切片里缺失，已从第 10 讲保留。
- 未改课件源文件；本目录为独立完整工程副本。
