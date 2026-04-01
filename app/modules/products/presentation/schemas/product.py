from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    image: str | None = Field(default=None, max_length=2048)
    category_id: int = Field(ge=1)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    image: str | None = Field(default=None, max_length=2048)
    category_id: int | None = Field(default=None, ge=1)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    image: str | None
    category_id: int
    category_name: str
    created_at: datetime
    out_of_stock: bool

    @classmethod
    def from_product(cls, p) -> ProductResponse:
        cat_name = p.category.name if getattr(p, "category", None) is not None else ""
        return cls(
            id=p.id,
            name=p.name,
            description=p.description,
            price=p.price,
            stock=p.stock,
            image=p.image,
            category_id=p.category_id,
            category_name=cat_name,
            created_at=p.created_at,
            out_of_stock=p.stock <= 0,
        )


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    limit: int
    offset: int
