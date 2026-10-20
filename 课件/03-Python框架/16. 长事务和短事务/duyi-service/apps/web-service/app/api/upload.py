from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.upload import UploadSignRequest, UploadSignResponse
from app.service.upload_service import UploadService

router = APIRouter(prefix="/api/upload", tags=["文件上传"])


@router.post("/sign", response_model=UploadSignResponse)
async def get_upload_sign(
    data: UploadSignRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await UploadService(db).generate_upload_sign(
        filename=data.filename, file_size=data.file_size
    )
