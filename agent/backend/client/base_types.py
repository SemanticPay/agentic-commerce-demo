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


class BuyerIdentity(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    email: str | None = None
    phone: str | None = None


class Address(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    country_code: str | None = Field(default=None, alias="countryCode")
    zip: str | None = None
    phone: str | None = None
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")


class CartAddressInput(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
    delivery_address: Address = Field(alias="deliveryAddress")


class AddressOption(BaseModel):
    address: CartAddressInput
    selected: bool


class CartDeliveryInput(BaseModel):
    addresses: list[AddressOption] | None = None


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
    buyer_identity: BuyerIdentity | None = Field(default=None, alias="buyerIdentity")
    delivery: CartDeliveryInput | None = None


class CartCreateResponse(BaseModel):
    cart: Cart | None = None
    user_errors: list[UserError] = Field(default=[], alias="userErrors")
    warnings: list[CartWarning] = Field(default=[])
