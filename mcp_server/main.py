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


mcp = FastMCP("SemanticPay Shopping Server")
shopify_client = ShopifyGraphQLClient()

@mcp.tool()
def search(query: str = "") -> list[Product]:
    resp = shopify_client.search_products(query=query) 

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
def create_cart():
    pass  

@mcp.tool()
def get_cart():
    pass


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
