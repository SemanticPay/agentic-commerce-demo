from typing import Any
from pydantic import BaseModel
from base_types import Item, Cart
from enum import Enum

class WidgetType(str, Enum):
    ITEM = "item"
    CART = "cart"

class Widget(BaseModel):
    type: str
    data: Any

class ItemWidget(Widget):
    type: str = WidgetType.ITEM
    data: Item

class CartWidget(Widget):
    type: str = WidgetType.CART
    data: Cart

