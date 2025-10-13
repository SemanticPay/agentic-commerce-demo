"""
SemanticPay MCP Shopping Server.

This module provides a Model Context Protocol (MCP) server that exposes e-commerce
shopping functionality through standardized tools. It acts as a bridge between
AI agents and e-commerce platforms (like Shopify), allowing AI assistants to
search for products, create shopping carts, and manage checkout processes.

Overview:
    The server implements three primary MCP tools that enable AI agents to provide
    complete shopping assistance:
    
    1. search_products: Find products by natural language query
       - Searches the store's product catalog
       - Returns product IDs, titles, descriptions, images, and prices
       - Supports empty query to browse all products
    
    2. cart_create: Create a cart with items and customer info
       - Requires product IDs (from search), quantities, buyer info, and delivery address
       - Returns cart with checkout URL and pricing breakdown
       - Validates inventory and calculates totals including tax
    
    3. cart_get: Retrieve existing cart by ID
       - Fetches current cart state including updated pricing
       - Useful for resuming shopping sessions
       - Returns same structure as cart_create

Architecture:
    MCP Server (FastMCP) ← this module
        ↓ exposes tools via HTTP transport
    AI Agent (Claude, GPT, etc.)
        ↓ calls tools with structured requests
    StoreFrontClient Interface (abstract)
        ↓ implemented by provider-specific clients
    E-commerce Platform (Shopify, WooCommerce, etc.)
    
    Components:
    - FastMCP: Handles MCP protocol communication and tool registration
    - StoreFrontClient: Platform-agnostic interface for e-commerce operations
    - Factory Pattern: Allows runtime selection of store provider
    - Type Models: Transform between MCP schemas and internal data structures

Data Flow:
    1. AI agent requests search via MCP tool call
    2. MCP server receives request, validates parameters
    3. Server calls StoreFrontClient.search_products()
    4. Client makes platform-specific API call (e.g., Shopify GraphQL)
    5. Client transforms platform response to standard models
    6. Server transforms to MCP response models
    7. Response sent back to AI agent via MCP protocol

Configuration:
    The server is configured at module level to connect to a specific store:
    
    >>> storefront_client = get_storefront_client(
    ...     provider=StoreProvider.SHOPIFY,  # Platform type
    ...     store_url="https://mystore.myshopify.com/api/2025-10/graphql.json",
    ...     access_token="storefront_access_token"  # Optional for public access
    ... )
    
    To connect to a different store or platform:
    - Change the provider (when other providers are implemented)
    - Update the store_url to point to your store's API endpoint
    - Provide appropriate authentication credentials in provider_kwargs

Running the Server:
    Run as a standalone script to start the HTTP MCP server:
    
    >>> python main.py
    
    The server starts on http://0.0.0.0:8000 and listens for MCP requests.
    AI agents can connect to this endpoint to use the shopping tools.

AI Agent Usage:
    AI agents (like Claude with MCP support) can connect to this server and
    use the exposed tools to provide shopping assistance:
    
    User: "I'm looking for a blue bag"
    Agent: [calls search_products(query="blue bag")]
    Agent: "I found 3 options... [shows results]"
    User: "I'll take the Ocean Blue Tote"
    Agent: [collects shipping info and email]
    Agent: [calls cart_create(...)]
    Agent: "Your cart is ready! Total: $45.99. Checkout here: [URL]"

Error Handling:
    - Tool functions may raise exceptions for API failures
    - FastMCP automatically converts exceptions to MCP error responses
    - Client implementations should provide clear error messages
    - Invalid product IDs, expired carts, and network errors are handled gracefully

Security Considerations:
    - Store access tokens should be kept secure and not exposed to clients
    - The MCP server acts as a trusted intermediary between AI and store APIs
    - Consider running behind authentication/authorization if exposed publicly
    - Cart checkout URLs are temporary and expire after inactivity

Dependencies:
    - fastmcp: MCP server framework (https://github.com/jlowin/fastmcp)
    - pydantic: Data validation and serialization
    - Platform-specific clients (e.g., Shopify GraphQL client)

See Also:
    - FastMCP documentation: https://github.com/jlowin/fastmcp
    - MCP specification: https://modelcontextprotocol.io
    - StoreFrontClient interface: mcp_server/client/interface.py
    - Base type definitions: mcp_server/base_types.py
"""

import logging
import sys
from datetime import datetime

from fastmcp import FastMCP
from mcp_server.base_types import (
    Price,
    Product,
    Cart,
    ProductList,
)
from mcp_server.client.base_types import Address, AddressOption, BuyerIdentity, CartAddressInput, CartCreateRequest, CartDeliveryInput, CartGetRequest, CartLineInput, SearchProductsRequest, StoreProvider
from mcp_server.client.factory import get_storefront_client
from mcp_server.client.interface import StoreFrontClient

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# Initialize MCP server
logger.info("Initializing SemanticPay Shopping Server")
mcp = FastMCP("SemanticPay Shopping Server")
logger.info("MCP server initialized successfully")

# Initialize storefront client with Shopify
# To use a different store, modify the provider and kwargs here
logger.info("Initializing Shopify storefront client")
storefront_client: StoreFrontClient = get_storefront_client(
    provider=StoreProvider.SHOPIFY,
    store_url="https://huescorner.myshopify.com/api/2025-10/graphql.json",
)
logger.info("Storefront client initialized successfully")

@mcp.tool(
    name="search_products",
    description="""Search for products in the store catalog.
    
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
        ProductList: Object containing:
            - products (list[Product]): List of matching products, each containing:
                - id (str): Unique product identifier (use this for cart_create)
                - title (str): Product name/title
                - description (str): Detailed product description (may contain HTML)
                - image_url (str): URL to product image for display
                - price (Price): Product price with amount and currency_code
    
    Example AI Conversation Flow:
        User: "I'm looking for a blue bag"
        AI: [calls search_products(query="blue bag")]
        AI: "I found 3 blue bags:
             1. Ocean Blue Tote - $45.99
             2. Navy Backpack - $67.50
             3. Sapphire Clutch - $32.00
             Would you like more details on any of these?"
    
    Example Usage:
        >>> # Search for specific products
        >>> results = search_products(query="laptop")
        >>> for product in results.products:
        ...     print(f"{product.title}: ${product.price.amount} {product.price.currency_code}")
        >>> 
        >>> # Get all products
        >>> all_results = search_products()
        >>> print(f"Found {len(all_results.products)} total products")
    
    Note:
        - Search behavior depends on the underlying store platform
        - Results are limited (typically 10-250 products per query)
        - Price includes both amount and currency code (not just a float)
        - Image URL can be displayed to user or embedded in rich responses
        - Return type is ProductList containing a list, not a direct list
    """,
    output_schema=ProductList.model_json_schema(),
)
def search_products(query: str = "") -> ProductList:
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
        ProductList: Object containing:
            - products (list[Product]): List of matching products, each containing:
                - id (str): Unique product identifier (use this for cart_create)
                - title (str): Product name/title
                - description (str): Detailed product description (may contain HTML)
                - image_url (str): URL to product image for display
                - price (Price): Product price with amount and currency_code
    
    Example AI Conversation Flow:
        User: "I'm looking for a blue bag"
        AI: [calls search_products(query="blue bag")]
        AI: "I found 3 blue bags:
             1. Ocean Blue Tote - $45.99
             2. Navy Backpack - $67.50
             3. Sapphire Clutch - $32.00
             Would you like more details on any of these?"
    
    Example Usage:
        >>> # Search for specific products
        >>> results = search_products(query="laptop")
        >>> for product in results.products:
        ...     print(f"{product.title}: ${product.price.amount} {product.price.currency_code}")
        >>> 
        >>> # Get all products
        >>> all_results = search_products()
        >>> print(f"Found {len(all_results.products)} total products")
    
    Note:
        - Search behavior depends on the underlying store platform
        - Results are limited (typically 10-250 products per query)
        - Price includes both amount and currency code (not just a float)
        - Image URL can be displayed to user or embedded in rich responses
        - Return type is ProductList containing a list, not a direct list
    """
    logger.info(f"search_products called with query: '{query}'")
    
    try:
        logger.info("Sending search request to storefront client")
        resp = storefront_client.search_products(SearchProductsRequest(query=query))
        logger.info(f"Received response with {len(resp.products)} products")

        prod_list = ProductList()
        logger.info("Processing products and variants")
        
        for idx, prod in enumerate(resp.products):
            logger.debug(f"Processing product {idx + 1}/{len(resp.products)}: {prod.title}")
            for variant_idx, variant in enumerate(prod.variants):
                product = Product(
                    id=variant.id,
                    title=f"{prod.title} - {variant.title}",
                    description=prod.description,
                    image_url=prod.images[0],
                    price=Price(
                        amount=variant.price.amount,
                        currency_code=variant.price.currency_code,
                    ),
                )
                prod_list.products.append(product)
                logger.debug(f"Added variant {variant_idx + 1}: {product.title} - {product.price.amount} {product.price.currency_code}")

        logger.info(f"Successfully processed {len(prod_list.products)} product variants")
        return prod_list
    
    except Exception as e:
        logger.error(f"Error in search_products: {str(e)}", exc_info=True)
        raise

@mcp.tool(
    name="cart_create",
    description="""Create a shopping cart with items and customer information.
    
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
            to quantities. Product IDs come from search_products() results.
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
            - checkout_url (str): Direct URL to complete checkout
            - subtotal_amount (Price): Cart subtotal before tax
            - tax_amount (Price | None): Tax amount if calculated
            - total_amount (Price): Final total amount
    
    Example AI Conversation Flow:
        User: "I want to buy the Ocean Blue Tote"
        AI: [calls search_products(query="Ocean Blue Tote")]
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
        >>> print(f"Cart created! Checkout here: {cart.checkout_url}")
        >>> print(f"Total: ${cart.total_amount.amount}")
    
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
    """,
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
            to quantities. Product IDs come from search_products() results.
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
            - checkout_url (str): Direct URL to complete checkout
            - subtotal_amount (Price): Cart subtotal before tax
            - tax_amount (Price | None): Tax amount if calculated
            - total_amount (Price): Final total amount
    
    Example AI Conversation Flow:
        User: "I want to buy the Ocean Blue Tote"
        AI: [calls search_products(query="Ocean Blue Tote")]
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
        >>> print(f"Cart created! Checkout here: {cart.checkout_url}")
        >>> print(f"Total: ${cart.total_amount.amount}")
    
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
    logger.info("cart_create called")
    logger.info(f"Items requested: {len(item_id_to_quantity)} product(s)")
    logger.info(f"Buyer email: {buyer_email}")
    logger.info(f"Delivery to: {delivery_address_first_name} {delivery_address_last_name}, {delivery_address_city}, {delivery_address_country_code}")
    
    try:
        logger.info("Building cart line items")
        lines = []
        for item_id, quantity in item_id_to_quantity.items():
            lines.append(CartLineInput(
                quantity=quantity,
                merchandiseId=item_id,
            ))
            logger.debug(f"Added line item: {item_id} (qty: {quantity})")
        logger.info(f"Created {len(lines)} cart line item(s)")

        logger.info("Building buyer identity")
        buyer_identity = BuyerIdentity(
            email=buyer_email,
            phone=buyer_phone,
        )
        logger.info("Buyer identity created successfully")

        logger.info("Building delivery address")
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
        logger.info("Delivery address created successfully")

        logger.info("Sending cart creation request to storefront client")
        resp = storefront_client.cart_create(req=CartCreateRequest(
            lines=lines,
            buyerIdentity=buyer_identity,
            delivery=delivery,
        ))
        logger.info("Cart created successfully on storefront")

        logger.info("Building cart response object")
        cart = Cart(
            checkout_url=resp.cart.checkout_url, 
            subtotal_amount=Price(
                amount=resp.cart.cost.subtotal_amount.amount,
                currency_code=resp.cart.cost.subtotal_amount.currency_code,
            ),
            tax_amount=Price(
                amount=resp.cart.cost.total_tax_amount.amount,
                currency_code=resp.cart.cost.total_tax_amount.currency_code,
            ) if resp.cart.cost.total_tax_amount else None,
            total_amount=Price(
                amount=resp.cart.cost.total_amount.amount,
                currency_code=resp.cart.cost.total_amount.currency_code,
            ),
        )
        
        logger.info(f"Cart created - Subtotal: {cart.subtotal_amount.amount} {cart.subtotal_amount.currency_code}")
        if cart.tax_amount:
            logger.info(f"Tax: {cart.tax_amount.amount} {cart.tax_amount.currency_code}")
        logger.info(f"Total: {cart.total_amount.amount} {cart.total_amount.currency_code}")
        logger.info(f"Checkout URL: {cart.checkout_url}")

        return cart
    
    except Exception as e:
        logger.error(f"Error in cart_create: {str(e)}", exc_info=True)
        raise

@mcp.tool(
    name="cart_get",
    description="""Retrieve an existing shopping cart by its unique identifier.
    
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
            - checkout_url (str): URL to complete checkout
            - subtotal_amount (Price): Cart subtotal before tax
            - tax_amount (Price | None): Tax amount if calculated
            - total_amount (Price): Final total amount
    
    Example AI Conversation Flow:
        User: "What's in my cart?"
        AI: [calls cart_get(cart_id="gid://shopify/Cart/abc123")]
        AI: "Your cart total is $91.98 (subtotal: $85.00, tax: $6.98).
             Ready to checkout? Here's your link: [checkout_url]"
        
        User: "Can you check my cart from earlier?"
        AI: [calls cart_get with saved cart_id]
        AI: [if error] "I couldn't find that cart - it may have expired.
             Would you like to create a new one?"
    
    Example Usage:
        >>> # Get a cart by ID
        >>> cart = cart_get(cart_id="gid://shopify/Cart/abc123")
        >>> print(f"Subtotal: ${cart.subtotal_amount.amount}")
        >>> print(f"Tax: ${cart.tax_amount.amount if cart.tax_amount else 0}")
        >>> print(f"Total: ${cart.total_amount.amount}")
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
    """,
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
            - checkout_url (str): URL to complete checkout
            - subtotal_amount (Price): Cart subtotal before tax
            - tax_amount (Price | None): Tax amount if calculated
            - total_amount (Price): Final total amount
    
    Example AI Conversation Flow:
        User: "What's in my cart?"
        AI: [calls cart_get(cart_id="gid://shopify/Cart/abc123")]
        AI: "Your cart total is $91.98 (subtotal: $85.00, tax: $6.98).
             Ready to checkout? Here's your link: [checkout_url]"
        
        User: "Can you check my cart from earlier?"
        AI: [calls cart_get with saved cart_id]
        AI: [if error] "I couldn't find that cart - it may have expired.
             Would you like to create a new one?"
    
    Example Usage:
        >>> # Get a cart by ID
        >>> cart = cart_get(cart_id="gid://shopify/Cart/abc123")
        >>> print(f"Subtotal: ${cart.subtotal_amount.amount}")
        >>> print(f"Tax: ${cart.tax_amount.amount if cart.tax_amount else 0}")
        >>> print(f"Total: ${cart.total_amount.amount}")
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
    logger.info(f"cart_get called with cart_id: {cart_id}")
    
    try:
        logger.info("Sending cart retrieval request to storefront client")
        resp = storefront_client.cart_get(req=CartGetRequest(id=cart_id))
        logger.info("Cart retrieved successfully from storefront")

        logger.info("Building cart response object")
        cart = Cart(
            checkout_url=resp.cart.checkout_url, 
            subtotal_amount=Price(
                amount=resp.cart.cost.subtotal_amount.amount,
                currency_code=resp.cart.cost.subtotal_amount.currency_code,
            ),
            tax_amount=Price(
                amount=resp.cart.cost.total_tax_amount.amount,
                currency_code=resp.cart.cost.total_tax_amount.currency_code,
            ) if resp.cart.cost.total_tax_amount else None,
            total_amount=Price(
                amount=resp.cart.cost.total_amount.amount,
                currency_code=resp.cart.cost.total_amount.currency_code,
            ),
        )
        
        logger.info(f"Cart retrieved - Subtotal: {cart.subtotal_amount.amount} {cart.subtotal_amount.currency_code}")
        if cart.tax_amount:
            logger.info(f"Tax: {cart.tax_amount.amount} {cart.tax_amount.currency_code}")
        logger.info(f"Total: {cart.total_amount.amount} {cart.total_amount.currency_code}")
        logger.info(f"Checkout URL: {cart.checkout_url}")

        return cart
    
    except Exception as e:
        logger.error(f"Error in cart_get: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Starting SemanticPay MCP Shopping Server")
    logger.info("="*60)
    print()
    logger.info("Running MCP server on http://0.0.0.0:8000")
    mcp.run(transport="http", host="0.0.0.0", port=8000)
