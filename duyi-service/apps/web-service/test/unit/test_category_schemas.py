from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schema.category import (
    CategoryCreate,
    CategoryDetailResponse,
    CategoryResponse,
    CategoryUpdate,
)
from app.schema.product import ProductBrief


class TestCategoryCreate:
    @pytest.mark.smoke
    def test_valid_create_with_all_fields(self):
        c = CategoryCreate(name="Electronics", description="电子数码产品")
        assert c.name == "Electronics"
        assert c.description == "电子数码产品"

    def test_default_description_is_empty(self):
        c = CategoryCreate(name="Books")
        assert c.name == "Books"
        assert c.description == ""

    def test_empty_name_fails(self):
        with pytest.raises(ValidationError) as exc:
            CategoryCreate(name="")  # pyright: ignore[reportCallIssue]
        assert "String should have at least 1 character" in str(exc.value)

    def test_name_too_long_fails(self):
        with pytest.raises(ValidationError) as exc:
            CategoryCreate(name="x" * 51)  # pyright: ignore[reportCallIssue]
        assert "String should have at most 50 characters" in str(exc.value)

    def test_missing_name_fails(self):
        with pytest.raises(ValidationError):
            CategoryCreate(description="desc")  # pyright: ignore[reportCallIssue]


class TestCategoryUpdate:
    def test_all_fields_optional(self):
        c = CategoryUpdate()
        assert c.name is None
        assert c.description is None

    def test_partial_update_name_only(self):
        c = CategoryUpdate(name="NewName")
        assert c.name == "NewName"
        assert c.description is None

    def test_partial_update_description_only(self):
        c = CategoryUpdate(description="New description")
        assert c.name is None
        assert c.description == "New description"

    def test_name_constraints_still_apply(self):
        with pytest.raises(ValidationError):
            CategoryUpdate(name="x" * 51)  # pyright: ignore[reportCallIssue]


class TestCategoryResponse:
    def test_from_attributes_config(self):
        assert CategoryResponse.model_config.get("from_attributes") is True

    def test_basic_response(self):
        r = CategoryResponse(id=1, name="Books", description="All kinds of books")
        assert r.id == 1
        assert r.name == "Books"
        assert r.description == "All kinds of books"

    def test_missing_required_field_fails(self):
        with pytest.raises(ValidationError):
            CategoryResponse(id=1, name="Books")  # pyright: ignore[reportCallIssue]


class TestCategoryDetailResponse:
    def test_from_attributes_config(self):
        assert CategoryDetailResponse.model_config.get("from_attributes") is True

    def test_empty_products_default(self):
        r = CategoryDetailResponse(id=1, name="Books", description="desc")
        assert r.products == []

    def test_with_products(self):
        now = datetime.now(timezone.utc)
        r = CategoryDetailResponse(
            id=1,
            name="Books",
            description="desc",
            products=[
                ProductBrief(id=10, name="Dune", description="scifi", brand=None, created_at=now)
            ],
        )
        assert len(r.products) == 1
        assert r.products[0].name == "Dune"
        assert r.products[0].brand is None
