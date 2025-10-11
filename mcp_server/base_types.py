from pydantic import BaseModel


class Product(BaseModel):
    id: str
    title: str
    description: str
    price: float
    image_url: str


class Cart(BaseModel):
    products: list[Product]
    final_price: float

