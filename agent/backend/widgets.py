from typing import Any
from pydantic import BaseModel
from enum import Enum

class WidgetType(str, Enum):
    PRODUCT = "product"
    CART = "cart"

class Widget(BaseModel):
    type: str
    data: Any
