from datetime import datetime
from pydantic import BaseModel


# 1. 定义数据模型（就像一个表单模板）
class User(BaseModel):
    id: int  # 要求必须是整数
    name: str = "John Doe"  # 字符串，且有默认值
    signup_ts: datetime | None = None  # 可以是日期时间或空
    friends: list[int] = []  # 整数列表


# 2. 输入外部数据（通常是 API 请求或文件读取）
# 注意：这里的 'id' 是字符串 '123'，'friends' 中包含了字符串和字节数据
external_data = {
    "id": "123",
    "signup_ts": "2024-06-01 12:22",
    "friends": [1, "2", b"3"],
}

# 3. Pydantic 进行验证和转换
user = User(**external_data)

# # 4. 打印结果
print(user)
# > User id=123 name='John Doe' signup_ts=datetime.datetime(2024, 6, 1, 12, 22) friends=[1, 2, 3]
print(user.id)
# > 123 (这里已经是整数类型，不再是字符串)
print(user.friends)
# > [1, 2, 3]
