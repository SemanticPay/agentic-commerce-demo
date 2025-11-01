from pydantic import BaseModel, Field
from typing import Any, Optional
from enum import Enum


class Price(BaseModel):
    amount: float
    currency_code: str


class Product(BaseModel):
    id: str
    variant_id: str
    title: str
    description: str
    price: Price
    image: str


class ProductList(BaseModel):
    products: list[Product] = Field(default_factory=list)


class ProductSection(BaseModel):
    title: str
    subtitle: str
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

class SearchCategory(BaseModel):
    title: str
    subtitle: str
    description: str
    query: str

class StateCartProduct(BaseModel):
    id: str
    variant_id: str
    quantity: int
    title: str
    description: str
    image_url: str
    price: Price

class StateCart(BaseModel):
    id_to_product: dict[str, StateCartProduct] = Field(default_factory=dict)

