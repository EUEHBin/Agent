from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schema.product import SkuBrief
from app.schema.sku import SkuCreate, SkuResponse, SkuUpdate


class TestSkuBrief:
    def test_from_attributes_config(self):
        assert SkuBrief.model_config.get("from_attributes") is True

    def test_price_is_decimal(self):
        s = SkuBrief(
            id=1, sku_code="SKU001", price=Decimal("99.99"), stock=10,
            attrs={"color": "red"}, image_url="http://img",
        )
        assert isinstance(s.price, Decimal)
        assert s.price == Decimal("99.99")


class TestSkuCreate:
    @pytest.mark.smoke
    def test_valid_create_with_all_fields(self):
        s = SkuCreate(
            sku_code="SKU-001",
            price=Decimal("199.99"),
            stock=100,
            attrs={"color": "red", "size": "XL"},
            image_url="https://img.example.com/1.jpg",
        )
        assert s.sku_code == "SKU-001"
        assert s.price == Decimal("199.99")
        assert s.stock == 100
        assert s.attrs == {"color": "red", "size": "XL"}

    def test_default_stock_is_zero(self):
        s = SkuCreate(
            sku_code="SKU-X",
            price=Decimal("10"),
            attrs={},
            image_url="http://x",
        )
        assert s.stock == 0

    def test_negative_price_fails(self):
        with pytest.raises(ValidationError) as exc:
            SkuCreate(
                sku_code="SKU-X",
                price=Decimal("-0.01"),
                attrs={},
                image_url="http://x",
            )
        assert "greater than or equal to 0" in str(exc.value)

    def test_negative_stock_fails(self):
        with pytest.raises(ValidationError) as exc:
            SkuCreate(
                sku_code="SKU-X",
                price=Decimal("10"),
                stock=-1,
                attrs={},
                image_url="http://x",
            )
        assert "greater than or equal to 0" in str(exc.value)

    def test_missing_sku_code_fails(self):
        with pytest.raises(ValidationError):
            SkuCreate(price=Decimal("10"), attrs={}, image_url="http://x")  # pyright: ignore[reportCallIssue]

    def test_missing_attrs_fails(self):
        with pytest.raises(ValidationError):
            SkuCreate(sku_code="S", price=Decimal("10"), image_url="http://x")  # pyright: ignore[reportCallIssue]

    def test_missing_price_fails(self):
        with pytest.raises(ValidationError):
            SkuCreate(sku_code="S", attrs={}, image_url="http://x")  # pyright: ignore[reportCallIssue]

    def test_empty_sku_code_fails(self):
        with pytest.raises(ValidationError):
            SkuCreate(sku_code="", price=Decimal("10"), attrs={}, image_url="http://x")  # pyright: ignore[reportCallIssue]

    def test_sku_code_too_long_fails(self):
        with pytest.raises(ValidationError):
            SkuCreate(sku_code="x" * 51, price=Decimal("10"), attrs={}, image_url="http://x")  # pyright: ignore[reportCallIssue]

    def test_zero_price_is_valid(self):
        s = SkuCreate(sku_code="S", price=Decimal("0"), attrs={}, image_url="http://x")
        assert s.price == Decimal("0")

    def test_attrs_accepts_arbitrary_dict(self):
        s = SkuCreate(
            sku_code="S",
            price=Decimal("10"),
            attrs={"material": "cotton", "weight": 200, "tags": ["a", "b"]},
            image_url="http://x",
        )
        assert s.attrs["material"] == "cotton"
        assert s.attrs["weight"] == 200
        assert s.attrs["tags"] == ["a", "b"]


class TestSkuUpdate:
    def test_all_fields_optional(self):
        s = SkuUpdate()
        assert s.sku_code is None
        assert s.price is None
        assert s.stock is None
        assert s.attrs is None
        assert s.image_url is None

    def test_partial_update_price_only(self):
        s = SkuUpdate(price=Decimal("88.88"))
        assert s.price == Decimal("88.88")
        assert s.sku_code is None

    def test_negative_price_still_fails(self):
        with pytest.raises(ValidationError):
            SkuUpdate(price=Decimal("-1"))  # pyright: ignore[reportCallIssue]

    def test_negative_stock_still_fails(self):
        with pytest.raises(ValidationError):
            SkuUpdate(stock=-1)  # pyright: ignore[reportCallIssue]


class TestSkuResponse:
    def test_from_attributes_config(self):
        assert SkuResponse.model_config.get("from_attributes") is True

    def test_has_product_id(self):
        r = SkuResponse(
            id=1, product_id=100, sku_code="SKU001",
            price=Decimal("99"), stock=10, attrs={}, image_url="http://x",
        )
        assert r.product_id == 100
