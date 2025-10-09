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


# Cart creation

class Attribute(BaseModel):
    key: str
    value: str

class CartLineInput(BaseModel):
    attributes: list[Attribute] | None = None
    quantity: int
    merchandise_id: str = Field(alias="merchandiseId")
    selling_plan_id: str | None = Field(default=None, alias="sellingPlanId")
    parent: dict | None = None

class BuyerIdentity(BaseModel):
    email: str | None = None
    phone: str | None = None
    company_location_id: str | None = Field(default=None, alias="companyLocationId")
    country_code: str | None = Field(default=None, alias="countryCode")
    customer_access_token: str | None = Field(default=None, alias="customerAccessToken")
    preferences: dict | None = None

class CartDeliveryInput(BaseModel):
    addresses: list[dict] | None = None

class Metafield(BaseModel):
    key: str
    value: str
    type: str

class CartInput(BaseModel):
    attributes: list[Attribute] | None = None
    lines: list[CartLineInput] | None = None
    discount_codes: list[str] | None = Field(default=None, alias="discountCodes")
    gift_card_codes: list[str] | None = Field(default=None, alias="giftCardCodes")
    note: str | None = None
    buyer_identity: BuyerIdentity | None = Field(default=None, alias="buyerIdentity")
    delivery: CartDeliveryInput | None = None
    metafields: list[Metafield] | None = None

class UserError(BaseModel):
    field: list[str] | None = None
    message: str

class CartWarning(BaseModel):
    message: str

class Cart(BaseModel):
    id: str
    checkout_url: str = Field(alias="checkoutUrl")
    total_quantity: int = Field(alias="totalQuantity")
    cost: dict | None = None
    buyer_identity: BuyerIdentity | None = Field(default=None, alias="buyerIdentity")
    attributes: list[Attribute] | None = None
    discount_codes: list[dict] | None = Field(default=None, alias="discountCodes")
    note: str | None = None
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

class CartCreateResponse(BaseModel):
    cart: Cart | None = None
    user_errors: list[UserError] = Field(default=[], alias="userErrors")
    warnings: list[CartWarning] = Field(default=[])


