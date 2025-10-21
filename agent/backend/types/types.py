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


class QueryResponse(BaseModel):
    response: str
    status: str
    session_id: Optional[str] = None
    widgets: list[Any] = Field(default_factory=list)

class WidgetType(str, Enum):
    PRODUCT = "PRODUCT"
    CART = "CART"


class ProductWidget(Widget):
    pass


class CartWidget(Widget):
    pass
