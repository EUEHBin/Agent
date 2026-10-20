from pydantic import BaseModel, Field


class SettingUpdateItem(BaseModel):
    key: str = Field(min_length=1, description="设置键")
    value: str = Field(description="设置值")


class SettingItemResponse(BaseModel):
    key: str
    value: str
    display_name: str
    description: str

    model_config = {"from_attributes": True}


class SettingGroupResponse(BaseModel):
    key: str
    display_name: str
    description: str
    settings: list[SettingItemResponse] = []

    model_config = {"from_attributes": True}
