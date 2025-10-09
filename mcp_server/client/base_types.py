from pydantic import BaseModel, Field

class Price(BaseModel):
    amount: float
    currency_code: str = Field(alias="currencyCode")

class PriceRange(BaseModel):
    min_variant_price: Price = Field(alias="minVariantPrice")
    max_variant_price: Price = Field(alias="maxVariantPrice")

class ProductVariant(BaseModel):
    id: str
    title: str
    price: Price

class Product(BaseModel):
    id: str
    title: str
    description: str
    images: list[str]
    price: Price
    price_range: PriceRange | None = Field(default=None, alias="priceRange")
    variants: list[ProductVariant] | None = None

class SearchProductsResponse(BaseModel):
    products: list[Product]
