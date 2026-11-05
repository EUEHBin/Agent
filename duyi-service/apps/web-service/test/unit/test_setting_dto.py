import pytest
from pydantic import ValidationError

from app.schema.setting import (
    SettingUpdateItem,
    SettingItemResponse,
    SettingGroupResponse,
)


class TestSettingUpdateItem:
    @pytest.mark.smoke
    def test_valid_item(self):
        item = SettingUpdateItem(key="oss_endpoint", value="https://example.com")
        assert item.key == "oss_endpoint"
        assert item.value == "https://example.com"

    def test_empty_value_allowed(self):
        item = SettingUpdateItem(key="oss_endpoint", value="")
        assert item.value == ""

    def test_empty_key_fails(self):
        with pytest.raises(ValidationError) as exc:
            SettingUpdateItem(key="", value="x")  # pyright: ignore[reportCallIssue]
        assert "String should have at least 1 character" in str(exc.value)

    def test_missing_key_fails(self):
        with pytest.raises(ValidationError):
            SettingUpdateItem(value="x")  # pyright: ignore[reportCallIssue]

    def test_missing_value_fails(self):
        with pytest.raises(ValidationError):
            SettingUpdateItem(key="x")  # pyright: ignore[reportCallIssue]


class TestSettingItemResponse:
    def test_from_attributes_config(self):
        assert SettingItemResponse.model_config.get("from_attributes") is True

    def test_full_fields(self):
        r = SettingItemResponse(
            key="oss_endpoint",
            value="https://example.com",
            display_name="OSS Endpoint",
            description="描述",
        )
        assert r.key == "oss_endpoint"
        assert r.value == "https://example.com"
        assert r.display_name == "OSS Endpoint"
        assert r.description == "描述"

    def test_missing_required_fails(self):
        with pytest.raises(ValidationError):
            SettingItemResponse(key="k")  # pyright: ignore[reportCallIssue]


class TestSettingGroupResponse:
    def test_from_attributes_config(self):
        assert SettingGroupResponse.model_config.get("from_attributes") is True

    def test_empty_settings_default(self):
        r = SettingGroupResponse(
            key="aliyun_oss",
            display_name="阿里云OSS",
            description="OSS配置",
        )
        assert r.settings == []

    def test_with_settings(self):
        r = SettingGroupResponse(
            key="aliyun_oss",
            display_name="阿里云OSS",
            description="OSS配置",
            settings=[
                SettingItemResponse(
                    key="oss_endpoint",
                    value="",
                    display_name="Endpoint",
                    description="端点",
                ),
            ],
        )
        assert len(r.settings) == 1
        assert r.settings[0].key == "oss_endpoint"

    def test_missing_required_fails(self):
        with pytest.raises(ValidationError):
            SettingGroupResponse(key="k")  # pyright: ignore[reportCallIssue]
