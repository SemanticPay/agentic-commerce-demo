from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class StoreProvider(Enum):
    SHOPIFY = "SHOPIFY"


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
    online_store_url: str = Field(default="", alias="onlineStoreUrl")
    images: list[str]
    price: Price
    price_range: PriceRange | None = Field(default=None, alias="priceRange")
    variants: list[ProductVariant]


class SortKey(Enum):
    RELEVANCE = "RELEVANCE"


class CartLineInput(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    quantity: int
    merchandise_id: str = Field(alias="merchandiseId")


class UserError(BaseModel):
    field: list[str] | None = None
    message: str


class CartWarning(BaseModel):
    message: str


class Cost(BaseModel):
    subtotal_amount: Price = Field(alias="subtotalAmount")
    total_tax_amount: Price | None = Field(default=None, alias="totalTaxAmount")
    total_amount: Price = Field(alias="totalAmount")


class Cart(BaseModel):
    id: str
    checkout_url: str = Field(alias="checkoutUrl")
    total_quantity: int = Field(alias="totalQuantity")
    cost: Cost


# ============================================================================
# Search Operations
# ============================================================================


class SearchProductsRequest(BaseModel):
    query: str = ""
    first: int = 10
    sort_key: str = SortKey.RELEVANCE.value
    reverse: bool = False


class SearchProductsResponse(BaseModel):
    products: list[Product]


# ============================================================================
# Cart Get Operations
# ============================================================================


class CartGetRequest(BaseModel):
    id: str


class CartGetResponse(BaseModel):
    cart: Cart


# ============================================================================
# Cart Create Operations
# ============================================================================


class CartCreateRequest(BaseModel):
    lines: list[CartLineInput] | None = None


class CartCreateResponse(BaseModel):
    cart: Cart | None = None
    user_errors: list[UserError] = Field(default=[], alias="userErrors")
    warnings: list[CartWarning] = Field(default=[])


# ============================================================================
# Get Products Operations
# ============================================================================


class GetProductsRequest(BaseModel):
    num_results: int


class GetProductsResponse(BaseModel):
    products: list[Product]


# ============================================================================
# Get Product By ID/Handle Operations
# ============================================================================


class GetProductRequest(BaseModel):
    id: str


class GetProductResponse(BaseModel):
    product: Product | None
