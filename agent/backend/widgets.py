from typing import Any
from pydantic import BaseModel
from enum import Enum


class WidgetType(str, Enum):
    PRODUCT = "PRODUCT"
    CART = "CART"


class Widget(BaseModel):
    type: str
    data: Any


class ProductWidget(Widget):
    pass


class CartWidget(Widget):
    pass
