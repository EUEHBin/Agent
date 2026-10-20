from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schema.product import (
    CategoryBrief,
    ProductBrief,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    SkuBrief,
)


class TestProductCreate:
    @pytest.mark.smoke
    def test_valid_create_with_all_fields(self):
        p = ProductCreate(
            name="MacBook Pro",
            description="Apple laptop",
            brand="Apple",
            category_ids=[1, 2],
        )
        assert p.name == "MacBook Pro"
        assert p.description == "Apple laptop"
        assert p.brand == "Apple"
        assert p.category_ids == [1, 2]

    def test_minimal_create_name_only(self):
        p = ProductCreate(name="MacBook Pro")
        assert p.name == "MacBook Pro"
        assert p.description == ""
        assert p.brand is None
        assert p.category_ids == []

    def test_empty_name_fails(self):
        with pytest.raises(ValidationError) as exc:
            ProductCreate(name="")  # pyright: ignore[reportCallIssue]
        assert "String should have at least 1 character" in str(exc.value)

    def test_name_too_long_fails(self):
        with pytest.raises(ValidationError) as exc:
            ProductCreate(name="x" * 201)  # pyright: ignore[reportCallIssue]
        assert "String should have at most 200 characters" in str(exc.value)

    def test_missing_name_fails(self):
        with pytest.raises(ValidationError):
            ProductCreate(description="desc", brand="Apple")  # pyright: ignore[reportCallIssue]

    def test_default_category_ids_is_empty_list(self):
        p = ProductCreate(name="iPhone")
        assert p.category_ids == []

    def test_category_ids_with_non_int_fails(self):
        with pytest.raises(ValidationError):
            ProductCreate(name="iPhone", category_ids=["not_int"])  # pyright: ignore[reportCallIssue, reportArgumentType]


class TestProductUpdate:
    def test_all_fields_optional(self):
        p = ProductUpdate()
        assert p.name is None
        assert p.description is None
        assert p.brand is None
        assert p.category_ids is None

    def test_partial_update_name_only(self):
        p = ProductUpdate(name="New Name")
        assert p.name == "New Name"
        assert p.description is None
        assert p.brand is None
        assert p.category_ids is None

    def test_partial_update_category_ids_only(self):
        p = ProductUpdate(category_ids=[3, 4])
        assert p.category_ids == [3, 4]
        assert p.name is None

    def test_name_constraints_still_apply(self):
        with pytest.raises(ValidationError):
            ProductUpdate(name="x" * 201)  # pyright: ignore[reportCallIssue]

    def test_name_min_length_still_apply(self):
        with pytest.raises(ValidationError):
            ProductUpdate(name="")  # pyright: ignore[reportCallIssue]


class TestProductBrief:
    def test_from_attributes_config(self):
        assert ProductBrief.model_config.get("from_attributes") is True

    def test_brand_can_be_none(self):
        now = datetime.now(timezone.utc)
        p = ProductBrief(id=1, name="Test", description="desc", brand=None, created_at=now)
        assert p.brand is None

    def test_all_fields_present(self):
        now = datetime.now(timezone.utc)
        p = ProductBrief(id=42, name="Widget", description="A widget", brand="Acme", created_at=now)
        assert p.id == 42
        assert p.name == "Widget"
        assert p.description == "A widget"
        assert p.brand == "Acme"
        assert p.created_at == now


class TestProductResponse:
    def test_from_attributes_config(self):
        assert ProductResponse.model_config.get("from_attributes") is True

    def test_default_empty_categories_and_skus(self):
        now = datetime.now(timezone.utc)
        r = ProductResponse(
            id=1, name="Test", description="desc", brand=None,
            created_at=now, updated_at=now,
        )
        assert r.categories == []
        assert r.skus == []

    def test_with_nested_categories_and_skus(self):
        now = datetime.now(timezone.utc)
        r = ProductResponse(
            id=1,
            name="Test",
            description="desc",
            brand=None,
            created_at=now,
            updated_at=now,
            categories=[CategoryBrief(id=1, name="C1")],
            skus=[SkuBrief(
                id=10, sku_code="S1", price=Decimal("10"), stock=5,
                attrs={}, image_url="http://x",
            )],
        )
        assert len(r.categories) == 1
        assert r.categories[0].name == "C1"
        assert len(r.skus) == 1
        assert r.skus[0].sku_code == "S1"
        assert r.skus[0].price == Decimal("10")
