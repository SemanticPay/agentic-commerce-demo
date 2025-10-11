from fastmcp import FastMCP
from datetime import datetime
from base_types import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    Cart,
    CheckoutSession,
    DelegatePaymentRequest,
    DelegatePaymentResponse,
    FullfillmentAddress,
    Buyer,
    Order,
    Product,
)
from client.shopify import ShopifyGraphQLClient
from client.interface import StoreFrontClient
from mcp_server.client.base_types import Address, AddressOption, BuyerIdentity, CartAddressInput, CartCreateRequest, CartDeliveryInput, CartLineInput, SearchProductsRequest


mcp = FastMCP("SemanticPay Shopping Server")
shopify_client = ShopifyGraphQLClient(store_url="https://huescorner.myshopify.com/api/2025-10/graphql.json")

@mcp.tool()
def search(query: str = "") -> list[Product]:
    resp = shopify_client.search_products(SearchProductsRequest(query=query)) 

    products: list[Product] = []
    for prod in resp.products:
        products.append(Product(
            id=prod.id,
            title=prod.title,
            description=prod.description,
            image_url=prod.images[0],
            price=prod.price.amount,
        ))

    return products

@mcp.tool()
def cart_create():
    resp = shopify_client.cart_create(req=CartCreateRequest(
        lines=[
            CartLineInput(
                quantity=1,
                merchandise_id="gid://shopify/Product/7615715803342"
            ),
        ],
        buyerIdentity=BuyerIdentity(
            email="random@gmail.com",
            phone="1234",
        ),
        delivery=CartDeliveryInput(
            addresses=[
                AddressOption(
                    selected=True,
                    address=CartAddressInput(
                        deliveryAddress=Address(
                            city="Dubai",
                            country_code="AE",
                            first_name="John",
                            last_name="Doe",
                            address1="123 Main St",
                            address2="something",
                            zip="10001",
                            phone="1234567890", 
                        ),
                    )
                ),
            ]    
        ),
    ))

    # cart = Cart()

@mcp.tool()
def get_cart():
    pass


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
