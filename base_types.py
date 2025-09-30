from pydantic import BaseModel

class Item(BaseModel):
    id: int
    title: str
    description: str
    price: float

class Cart(BaseModel):
    items: list[Item]
    final_price: float

# Buyer includes and distilles "Address" and "Buyer" information from the ACP spec
# https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/main/spec/openapi/openapi.agentic_checkout.yaml
class Buyer(BaseModel):
    name: str
    email: str
    address: str
    phone_number: str
    city: str
    country: str
    postal_code: str

class CheckoutSession(BaseModel):
    id: str
    cart: Cart
    buyer: Buyer

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

class CheckoutSessionResponse(BaseModel):
    checkout_session: CheckoutSession

### /delegate_payment endpoint

