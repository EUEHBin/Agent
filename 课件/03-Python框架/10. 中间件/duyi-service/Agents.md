# duyi-service 工程说明

## 技术架构

基于 **UV Workspace** 构建的 Python 单体仓库（Monorepo），工作区成员为 `apps/*` 和 `packages/*`。Python 版本要求 `>=3.14`。

当前仅有一个子包：

### apps/web-service — Web Service

基于 **FastAPI** 的异步 Web 服务，使用 **SQLAlchemy**（async）+ **asyncpg** + **PostgreSQL** 作为数据存储，**Alembic** 管理数据库迁移，**Pydantic Settings** 管理配置。

目录结构：

| 目录 | 说明 |
|---|---|
| `app/main.py` | FastAPI 应用入口，注册路由、配置文档开关 |
| `app/core/` | 核心基础设施：`config.py`（环境变量配置）、`database.py`（异步引擎与会话工厂） |
| `app/model/` | SQLAlchemy ORM 模型：`base.py`（声明基类）、`product.py` / `category.py` / `sku.py` 等业务模型，`association/` 存放多对多关联表 |
| `app/schema/` | Pydantic 请求/响应模型 |
| `app/api/` | 路由处理器（`welcome.py`、`items.py`） |
| `migrations/` | Alembic 迁移脚本 |
| `test/` | 测试目录 |

## 沟通规范

**非常重要：当用户提问时，不能修改任何东西，不能新增任何东西，不能删除任何东西，仅回答用户问题即可**
