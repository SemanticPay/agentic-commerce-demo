from pydantic import BaseModel, Field
from typing import Optional


class UserPreferences(BaseModel):
    preferred_currency: str
    favorite_categories: list[str] = Field(default_factory=list)
    price_range: Optional[tuple[float, float]] = None
