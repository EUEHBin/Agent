# duyi-service 工程说明

## 技术架构

基于 **UV Workspace** 构建的 Python 单体仓库（Monorepo），工作区成员为 `apps/*` 和 `packages/*`。Python 版本要求 `>=3.14`。

当前包含两个子包：

### apps/web-service — Web Service

基于 **FastAPI** 的异步 Web 服务，使用 **SQLAlchemy**（async）+ **asyncpg** + **PostgreSQL** 作为数据存储，**Alembic** 管理数据库迁移，**Pydantic Settings** 管理配置。采用分层架构：路由层 (`api/`) → 业务逻辑层 (`service/`) → 数据访问层 (`model/`)。

目录结构：

| 目录 | 说明 |
|---|---|
| `app/main.py` | FastAPI 应用入口，注册路由、中间件、异常处理器、配置文档开关 |
| `app/api/` | 路由处理器：`auth.py`（认证）、`categories.py`（分类）、`products.py`（产品）、`settings.py`（设置）、`skus.py`（SKU）、`upload.py`（上传） |
| `app/core/` | 核心基础设施：`config.py`（环境变量配置）、`database.py`（异步引擎与会话工厂）、`auth.py`（认证逻辑）、`openapi.py`（OpenAPI 文档配置）、`middleware/`（CORS、请求耗时、响应包装） |
| `app/exception/` | 异常定义与全局异常处理器：`base.py`、`auth.py`、`database.py`、`not_found.py`、`upload.py`、`handler/`（统一错误响应与异常文档） |
| `app/model/` | SQLAlchemy ORM 模型：`base.py`（声明基类）、`product.py`、`category.py`、`sku.py`、`user.py`、`setting.py`、`setting_group.py`，`association/` 存放多对多关联表 |
| `app/schema/` | Pydantic 请求/响应模型：`product.py`、`category.py`、`sku.py`、`user.py`、`setting.py`、`upload.py` |
| `app/service/` | 业务逻辑层：`base.py`（基础服务类）、`product_service.py`、`category_service.py`、`sku_service.py`、`user_service.py`、`setting_service.py`、`upload_service.py` |
| `migrations/` | Alembic 迁移脚本（`env.py`、`versions/`） |
| `test/` | 测试目录，分三层：`unit/`（单元测试）、`integration/`（集成测试）、`e2e/`（端到端测试） |

### packages/duyi-utils — 共享工具库

Web Service 依赖的通用工具包，提供认证、上传、文件处理等复用模块。

目录结构：

| 目录 | 说明 |
|---|---|
| `src/duyi_utils/auth/` | 认证工具：`jwt_util.py`（JWT 生成/解析）、`password.py`（密码哈希/校验） |
| `src/duyi_utils/upload/` | 上传工具：`aliyun.py`（阿里云 OSS 上传）、`dir_strategy.py`（目录命名策略） |
| `src/duyi_utils/shared/` | 通用工具：`file_util.py`（文件操作）、`mime.py`（MIME 类型判断） |
| `test/unit/` | 单元测试 |
| `test/integration/` | 集成测试 |

## 常用命令

项目的常用命令通过 `Makefile` 管理：

| 命令 | 说明 |
|---|---|
| `make dev` | 启动开发服务器（端口 8080） |
| `make debug` | 启动调试模式（端口 8000，配合 debugpy） |
| `make test` | 运行全部测试（含覆盖率，阈值 80%） |
| `make test-unit` | 仅运行单元测试 |
| `make test-integration` | 仅运行集成测试 |
| `make test-e2e` | 仅运行端到端测试 |
| `make test-smoke` | 运行冒烟测试 |
| `make test-changed` | 仅运行与变更文件相关的测试 |
| `make db-migrate msg="..."` | 生成 Alembic 迁移脚本 |
| `make db-upgrade` | 执行数据库升级到最新版本 |
| `make db-downgrade version="-1"` | 回滚数据库版本 |

## 沟通规范

**非常重要：当用户提问时，不能修改任何东西，不能新增任何东西，不能删除任何东西，仅回答用户问题即可**

## 测试规则

**非常重要：写好测试脚本并运行后，如果测试没有全部通过，此时应停下，告诉用户失败的测试用例及其原因，由用户来判断是测试脚本的问题还是被测试代码的问题。绝对不能直接修改被测试的源代码。**
