"""
SemanticPay MCP Shopping Server.

This module provides a Model Context Protocol (MCP) server that exposes e-commerce
shopping functionality through standardized tools. It acts as a bridge between
AI agents and e-commerce platforms (like Shopify), allowing AI assistants to
search for products, create shopping carts, and manage checkout processes.

The server uses FastMCP to expose three main tools:
    1. search: Find products by query
    2. cart_create: Create a shopping cart with items and delivery info
    3. cart_get: Retrieve existing cart details

Architecture:
    - FastMCP server handles MCP protocol communication
    - StoreFrontClient provides platform-agnostic e-commerce operations
    - Factory pattern allows switching between different store providers
    - Tools transform between MCP schemas and internal data models

Configuration:
    The server is configured to connect to a Shopify store by default.
    Store URL and provider can be changed by modifying the storefront_client
    initialization.

Running the Server:
    >>> python main.py
    # Server starts on http://0.0.0.0:8000 with HTTP transport

AI Agent Usage:
    AI agents can connect to this MCP server and use the exposed tools to:
    - Search product catalogs
    - Build shopping carts for users
    - Retrieve cart information for checkout
    - Provide complete shopping assistance

See Also:
    - FastMCP documentation: https://github.com/jlowin/fastmcp
    - MCP specification: https://modelcontextprotocol.io
    - StoreFrontClient: Abstract interface for e-commerce operations
"""

from fastmcp import FastMCP
from base_types import (
    Product,
)
from client.base_types import Address, AddressOption, BuyerIdentity, Cart, CartAddressInput, CartCreateRequest, CartDeliveryInput, CartGetRequest, CartLineInput, SearchProductsRequest, StoreProvider
from client.factory import get_storefront_client
from client.interface import StoreFrontClient
from typing import List


# Initialize MCP server
mcp = FastMCP("SemanticPay Shopping Server")

# Initialize storefront client with Shopify
# To use a different store, modify the provider and kwargs here
storefront_client: StoreFrontClient = get_storefront_client(
    provider=StoreProvider.SHOPIFY,
    store_url="https://huescorner.myshopify.com/api/2025-10/graphql.json",
)

@mcp.tool(
    name="search_products",
    description=(
        "Search for products in the store catalog using keywords or phrases. "
        "Returns a list of products with IDs, titles, descriptions, images, and prices. "
        "Use this when users want to find or browse products. "
        "Empty query returns all products."
    ),
    output_schema={
        "type": "array",
        "items": Product.model_json_schema()
    }
)
def search(query: str = "") -> list[Product]:
    """Search for products in the store catalog.
    
    This MCP tool allows AI agents to search the e-commerce store's product
    catalog using natural language queries. It returns a list of matching
    products with essential information for display and purchase.
    
    **AI Agent Instructions:**
    - Use this tool when the user asks to find, search, or browse products
    - The query should be keywords or phrases (e.g., "red shoes", "laptop")
    - Empty query returns all products (use sparingly, can be many results)
    - Results include product ID (needed for cart_create), title, description,
      image URL, and price
    - Present results to user in a readable format with key details
    - If user wants more details, search again or use the product description
    
    Args:
        query (str): Search query text to match against product titles,
            descriptions, and tags. Can include multiple keywords.
            Examples: "running shoes", "blue bag", "laptop computer"
            Default: "" (returns all products)
    
    Returns:
        list[Product]: List of matching products, each containing:
            - id (str): Unique product identifier (use this for cart_create)
            - title (str): Product name/title
            - description (str): Detailed product description (may contain HTML)
            - image_url (str): URL to product image for display
            - price (float): Product price in store currency
    
    Example AI Conversation Flow:
        User: "I'm looking for a blue bag"
        AI: [calls search(query="blue bag")]
        AI: "I found 3 blue bags:
             1. Ocean Blue Tote - $45.99
             2. Navy Backpack - $67.50
             3. Sapphire Clutch - $32.00
             Would you like more details on any of these?"
    
    Example Usage:
        >>> # Search for specific products
        >>> products = search(query="laptop")
        >>> for product in products:
        ...     print(f"{product.title}: ${product.price}")
        >>> 
        >>> # Get all products
        >>> all_products = search()
    
    Note:
        - Search behavior depends on the underlying store platform
        - Results are limited (typically 10-250 products)
        - Price is returned as a float (store's default currency)
        - Image URL can be displayed to user or embedded in rich responses
    """
    resp = storefront_client.search_products(SearchProductsRequest(query=query)) 

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

@mcp.tool(
    name="create_shopping_cart",
    description=(
        "Create a new shopping cart with items, buyer information, and delivery address. "
        "Returns a cart with a unique ID and checkout URL. "
        "REQUIRED: item IDs with quantities, buyer email and phone (with country code), "
        "complete delivery address (city, country code, first/last name, street address, "
        "zip code, phone). Address line 2 is optional. "
        "Use this after collecting all required information from the user. "
        "Country codes must be ISO 3166-1 alpha-2 format (e.g., 'US', 'CA', 'GB')."
    ),
    output_schema=Cart.model_json_schema()
)
def cart_create(
    item_id_to_quantity: dict[str, int],

    buyer_email: str,
    buyer_phone: str,

    delivery_address_city: str,
    delivery_address_country_code: str,
    delivery_address_first_name: str,
    delivery_address_last_name: str,
    delivery_address_line1: str,
    delivery_address_line2: str | None,
    delivery_address_zip: str,
    delivery_address_phone: str,
) -> Cart:
    """Create a shopping cart with items and customer information.
    
    This MCP tool allows AI agents to create a complete shopping cart including
    line items, buyer identity, and delivery address. It returns a cart with a
    unique ID and checkout URL that the user can use to complete their purchase.
    
    **AI Agent Instructions:**
    - Use this tool after the user has selected products and provided their info
    - Collect ALL required information before calling this tool:
      1. Product IDs and quantities (from search results)
      2. Email and phone number
      3. Complete delivery address (all fields except address_line2)
    - Ask for missing information - don't make assumptions
    - The item_id should be the product.id from search results
    - After creating cart, provide the checkout URL to the user
    - Cart IDs expire after inactivity (typically 10-30 days)
    
    **Required Information Checklist:**
    ✓ Item IDs with quantities
    ✓ Buyer email
    ✓ Buyer phone (include country code, e.g., "+1234567890")
    ✓ Delivery city
    ✓ Delivery country code (ISO 3166-1, e.g., "US", "CA", "GB")
    ✓ Recipient first and last name
    ✓ Street address (line 1)
    ✓ ZIP/postal code
    ✓ Delivery phone number
    ✗ Address line 2 (optional - apartment, suite, etc.)
    
    Args:
        item_id_to_quantity (dict[str, int]): Dictionary mapping product IDs
            to quantities. Product IDs come from search() results.
            Example: {"gid://shopify/Product/123": 2, "gid://shopify/Product/456": 1}
        buyer_email (str): Customer's email address for order confirmation.
            Example: "customer@example.com"
        buyer_phone (str): Customer's phone number with country code.
            Example: "+12125551234" or "+44 20 1234 5678"
        delivery_address_city (str): Delivery city name.
            Example: "New York", "London", "Toronto"
        delivery_address_country_code (str): ISO 3166-1 alpha-2 country code.
            Examples: "US", "CA", "GB", "FR", "DE", "AU"
        delivery_address_first_name (str): Recipient's first name.
            Example: "John"
        delivery_address_last_name (str): Recipient's last name.
            Example: "Doe"
        delivery_address_line1 (str): Primary street address.
            Example: "123 Main Street", "45 Oxford Road"
        delivery_address_line2 (str | None): Optional secondary address line.
            Examples: "Apt 4B", "Suite 200", None
        delivery_address_zip (str): Postal/ZIP code.
            Examples: "10001", "SW1A 1AA", "M5H 2N2"
        delivery_address_phone (str): Contact phone for delivery.
            Example: "+12125551234"
    
    Returns:
        Cart: Created cart object containing:
            - id (str): Unique cart identifier (save this!)
            - checkout_url (str): Direct URL to complete checkout
            - total_quantity (int): Total items in cart
            - cost (Cost): Price breakdown (subtotal, tax, total)
    
    Example AI Conversation Flow:
        User: "I want to buy the Ocean Blue Tote"
        AI: [calls search(query="Ocean Blue Tote")]
        AI: "Great! I found it for $45.99. I'll need some information to create
             your cart. What's your email address?"
        User: "john@example.com"
        AI: "And your phone number with country code?"
        User: "+1 212 555 1234"
        AI: "What's your delivery address?"
        User: "123 Main St, Apt 4B, New York, NY 10001"
        AI: "And your name for delivery?"
        User: "John Doe"
        AI: [calls cart_create with all collected info]
        AI: "Perfect! I've created your cart with 1 item totaling $45.99.
             You can complete your purchase here: [checkout_url]"
    
    Example Usage:
        >>> cart = cart_create(
        ...     item_id_to_quantity={"gid://shopify/Product/123": 2},
        ...     buyer_email="customer@example.com",
        ...     buyer_phone="+12125551234",
        ...     delivery_address_city="New York",
        ...     delivery_address_country_code="US",
        ...     delivery_address_first_name="John",
        ...     delivery_address_last_name="Doe",
        ...     delivery_address_line1="123 Main Street",
        ...     delivery_address_line2="Apt 4B",
        ...     delivery_address_zip="10001",
        ...     delivery_address_phone="+12125551234"
        ... )
        >>> print(f"Cart created: {cart.checkout_url}")
    
    Raises:
        Exception: If cart creation fails due to:
            - Invalid product IDs
            - Out of stock items
            - Invalid address information
            - API communication errors
    
    Note:
        - All parameters except address_line2 are required
        - Phone numbers should include country code
        - Country codes must be valid ISO 3166-1 alpha-2 codes
        - Cart persists on server and can be retrieved with cart_get()
        - Checkout URL is a direct link - user doesn't need to log in
        - Prices and availability are validated at creation time
    """
    lines = []
    for item_id, quantity in item_id_to_quantity.items():
        lines.append(CartLineInput(
            quantity=quantity,
            merchandiseId=item_id,
        ))

    buyer_identity = BuyerIdentity(
        email=buyer_email,
        phone=buyer_phone,
    )

    delivery = CartDeliveryInput(
        addresses=[
            AddressOption(
                selected=True,
                address=CartAddressInput(
                    deliveryAddress=Address(
                        city=delivery_address_city,
                        countryCode=delivery_address_country_code,
                        firstName=delivery_address_first_name,
                        lastName=delivery_address_last_name,
                        address1=delivery_address_line1,
                        address2=delivery_address_line2,
                        zip=delivery_address_zip,
                        phone=delivery_address_phone, 
                    ),
                )
            ),
        ]    
    )

    resp = storefront_client.cart_create(req=CartCreateRequest(
        lines=lines,
        buyerIdentity=buyer_identity,
        delivery=delivery,
    ))

    return resp.cart

@mcp.tool(
    name="get_cart",
    description=(
        "Retrieve an existing shopping cart by its unique cart ID. "
        "Returns cart details including items, quantities, pricing, and checkout URL. "
        "Use this when users want to view their cart or resume a previous shopping session. "
        "Note: Carts may expire after 10-30 days of inactivity. "
        "If cart is not found, it may have expired - create a new one instead."
    ),
    output_schema=Cart.model_json_schema()
)
def cart_get(cart_id: str) -> Cart:
    """Retrieve an existing shopping cart by its unique identifier.
    
    This MCP tool allows AI agents to fetch the current state of a previously
    created cart, including all items, quantities, and pricing information.
    Useful for resuming shopping sessions or checking cart status.
    
    **AI Agent Instructions:**
    - Use this tool to retrieve a cart that was created earlier
    - The cart_id comes from the cart returned by cart_create()
    - Carts may expire after inactivity (typically 10-30 days)
    - If cart is not found, it may have expired - create a new one
    - Use this to show the user their current cart contents
    - Prices may have changed since cart creation
    
    **Common Use Cases:**
    1. User says "What's in my cart?" or "Show my cart"
    2. Resuming a previous shopping session
    3. Verifying cart contents before directing to checkout
    4. Checking updated prices or availability
    
    Args:
        cart_id (str): The unique cart identifier returned from cart_create().
            Format is platform-specific.
            Example: "gid://shopify/Cart/abc123def456"
    
    Returns:
        Cart: Cart object containing:
            - id (str): The cart identifier
            - checkout_url (str): URL to complete checkout
            - total_quantity (int): Total number of items in cart
            - cost (Cost): Current pricing with:
                - subtotal_amount (Price): Subtotal before tax
                - total_tax_amount (Price | None): Tax amount if calculated
                - total_amount (Price): Final total amount
    
    Example AI Conversation Flow:
        User: "What's in my cart?"
        AI: [calls cart_get(cart_id="gid://shopify/Cart/abc123")]
        AI: "Your cart has 2 items totaling $91.98:
             - Ocean Blue Tote (qty: 1) - $45.99
             - Navy Backpack (qty: 1) - $45.99
             Ready to checkout? Here's your link: [checkout_url]"
        
        User: "Can you check my cart from earlier?"
        AI: [calls cart_get with saved cart_id]
        AI: [if error] "I couldn't find that cart - it may have expired.
             Would you like to create a new one?"
    
    Example Usage:
        >>> # Get a cart by ID
        >>> cart = cart_get(cart_id="gid://shopify/Cart/abc123")
        >>> print(f"Cart has {cart.total_quantity} items")
        >>> print(f"Total: ${cart.cost.total_amount.amount}")
        >>> print(f"Checkout: {cart.checkout_url}")
    
    Raises:
        Exception: If cart retrieval fails due to:
            - Cart not found (invalid or expired ID)
            - Network/API errors
            - Invalid cart_id format
    
    Note:
        - Cart IDs are temporary and expire after inactivity
        - Prices may change between creation and retrieval
        - Out-of-stock items may be removed automatically by some platforms
        - The checkout URL remains valid as long as the cart exists
        - Some platforms may update tax calculations when retrieving cart
    """
    resp = storefront_client.cart_get(req=CartGetRequest(id=cart_id))
    return resp.cart


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
