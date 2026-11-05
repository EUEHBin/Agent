from pydantic import BaseModel, Field


class UploadSignRequest(BaseModel):
    filename: str = Field(min_length=1, description="文件名，如 photo.png")
    file_size: int = Field(gt=0, description="文件大小，单位字节")


class UploadSignResponse(BaseModel):
    host: str
    access_id: str
    policy: str
    signature: str
    key: str
    content_type: str
    bucket_domain: str
