from typing import Any
from pydantic import BaseModel
from base_types import Product, Cart
from enum import Enum

class WidgetType(str, Enum):
    PRODUCT = "product"
    CART = "cart"

class Widget(BaseModel):
    type: str
    data: Any

class ProductWidget(Widget):
    type: str = WidgetType.PRODUCT
    data: Product

class CartWidget(Widget):
    type: str = WidgetType.CART
    data: Cart

