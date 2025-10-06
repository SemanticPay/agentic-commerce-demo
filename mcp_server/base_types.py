from pydantic import BaseModel


class Item(BaseModel):
    id: int
    title: str
    description: str
    price: float


class Address(BaseModel):
    line_one: str
    line_two: str | None = None
    city: str
    state: str
    country: str
    postal_code: str


class Cart(BaseModel):
    items: list[Item]
    final_price: float


class PaymentMethod(BaseModel):
    type: str
    number: str
    exp_month: str
    exp_year: str
    name: str
    cvc: str


class Allowance(BaseModel):
    amount: float
    currency: str
    checkout_session_id: str
    merchant_id: str


class BillingAddress(Address):
    pass


class FullfillmentAddress(Address):
    pass


class Buyer(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str


class CheckoutSession(BaseModel):
    id: str
    cart: Cart
    buyer: Buyer
    fullfillment_address: FullfillmentAddress


### /search endpoint


class SearchRequest(BaseModel):
    query: str = ""
    keywords: str = ""


class SearchResponse(BaseModel):
    items: list[Item]


### /checkout_sessions endpoint


class CheckoutSessionRequest(BaseModel):
    item_ids: list[str]
    buyer: Buyer
    fullfillment_address: FullfillmentAddress


class CheckoutSessionResponse(BaseModel):
    checkout_session: CheckoutSession


### /delegate_payment endpoint


class DelegatePaymentRequest(BaseModel):
    payment_method: PaymentMethod
    allowance: Allowance
    billing_address: BillingAddress


class DelegatePaymentResponse(BaseModel):
    success: bool
    message: str = ""


class Order(BaseModel):
    checkout_session_id: str
    items: list[Item]
    buyer: Buyer
    fullfillment_address: FullfillmentAddress
    status: str  # "waiting_for_payment" or "done"
    created_at: str
    updated_at: str
