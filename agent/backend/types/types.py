from pydantic import BaseModel, Field
from typing import Any, Optional
from enum import Enum


class Price(BaseModel):
    amount: float
    currency_code: str


class Product(BaseModel):
    id: str
    title: str
    description: str
    price: Price
    image_url: str


class ProductList(BaseModel):
    products: list[Product] = Field(default_factory=list)


class ProductSection(BaseModel):
    title: str
    description: str
    products: list[Product] = Field(default_factory=list)


class Cart(BaseModel):
    checkout_url: str
    subtotal_amount: Price
    tax_amount: Price | None = None
    total_amount: Price


class FunctionPayload(BaseModel):
    name: str
    payload: Any | None = None


class AgentCallRequest(BaseModel):
    question: str
    session_id: str | None = None


class AgentCallResponse(BaseModel):
    answer: str
    function_payloads: list[FunctionPayload] = Field(default_factory=list)


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class Widget(BaseModel):
    type: str
    data: Any
    raw_html_string: str


class QueryResponse(BaseModel):
    response: str
    status: str
    session_id: Optional[str] = None
    widgets: list[Any] = Field(default_factory=list)

class WidgetType(str, Enum):
    PRODUCT = "PRODUCT"
    CART = "CART"
    PRODUCT_SECTIONS = "PRODUCT_SECTIONS"


class ProductWidget(Widget):
    pass


class CartWidget(Widget):
    pass


class UserPreferences(BaseModel):
    preferred_currency: str
    favorite_categories: list[str] = Field(default_factory=list)
    price_range: Optional[tuple[float, float]] = None


class AddToCartRequest(BaseModel):
    item_id: str
    quantity: int = 1
    session_id: Optional[str] = None

class AddToCartResponse(BaseModel):
    status: str
    session_id: Optional[str] = None

class RemoveFromCartRequest(BaseModel):
    item_id: str
    session_id: Optional[str] = None

class RemoveFromCartResponse(BaseModel):
    status: str
    session_id: Optional[str] = None
