from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Hello World", description="这是一个测试接口")
async def read_root():
    return {"Hello": "World"}
