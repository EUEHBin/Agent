import asyncio
from sqlalchemy import text
from app.model.engine import get_engine


async def test_connection():
    engine = get_engine()
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            print(f"✅ 异步连接 PostgreSQL 成功！查询结果: {value}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    finally:
        await engine.dispose()


# 运行异步函数
if __name__ == "__main__":
    asyncio.run(test_connection())
