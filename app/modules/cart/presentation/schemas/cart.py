from decimal import Decimal

from pydantic import BaseModel, Field


class CartAddRequest(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1)


class CartUpdateRequest(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=0)


class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: Decimal
    quantity: int
    total_price: Decimal


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_cart_price: Decimal
