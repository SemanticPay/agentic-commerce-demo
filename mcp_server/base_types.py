"""
MCP Server Public API Models.

This module defines the public-facing Pydantic models used for the Model Context Protocol
(MCP) server's tool interfaces. These models represent the data structures that AI agents
interact with when using the SemanticPay Shopping Server tools.

These models are simplified versions of the internal client models, designed to provide
a clean, easy-to-use interface for AI agents while hiding implementation complexity.

Models:
    Price: Represents a monetary amount with currency code.
        Used for all pricing information exposed to AI agents.
    
    Product: Product information returned by search results.
        Contains essential product details: ID, title, description, image, and price.
        Simplified from the internal Product model to include only fields needed
        for AI agent interactions.
    
    ProductList: Container for multiple products.
        Wrapper object for search results, containing a list of Product objects.
    
    Cart: Shopping cart summary with checkout information.
        Contains cart pricing breakdown and checkout URL. Returned by cart_create
        and cart_get tools. Does not include line item details to keep the interface
        simple - agents only need total pricing and the checkout URL.

Relationship to Internal Models:
    These models are the public API surface exposed through MCP tools. The main.py
    module transforms between these public models and the internal client models
    (from mcp_server.client.base_types) to maintain separation between the MCP
    interface and the underlying e-commerce client implementation.

Example:
    >>> # AI agent receives this structure from search_products tool
    >>> products = ProductList(
    ...     products=[
    ...         Product(
    ...             id="gid://shopify/Product/123",
    ...             title="Running Shoes",
    ...             description="Comfortable running shoes",
    ...             price=Price(amount=79.99, currency_code="USD"),
    ...             image_url="https://example.com/shoes.jpg"
    ...         )
    ...     ]
    ... )
    >>> 
    >>> # AI agent receives this structure from create_shopping_cart tool
    >>> cart = Cart(
    ...     checkout_url="https://store.com/cart/abc123",
    ...     subtotal_amount=Price(amount=79.99, currency_code="USD"),
    ...     tax_amount=Price(amount=7.20, currency_code="USD"),
    ...     total_amount=Price(amount=87.19, currency_code="USD")
    ... )

See Also:
    - main.py: MCP server implementation using these models
    - mcp_server.client.base_types: Internal client models
"""

from pydantic import BaseModel, Field


class Price(BaseModel):
    """Represents a monetary amount with its currency.
    
    Used for all pricing information in products and carts. Includes both the
    numeric amount and the ISO 4217 currency code for international support.
    
    Attributes:
        amount (float): The numeric price value (e.g., 19.99, 1234.50).
            Supports decimal precision for accurate pricing.
        currency_code (str): ISO 4217 three-letter currency code.
            Examples: "USD", "EUR", "GBP", "CAD", "AUD", "JPY"
    
    Example:
        >>> price = Price(amount=29.99, currency_code="USD")
        >>> price = Price(amount=24.99, currency_code="EUR")
        >>> print(f"${price.amount} {price.currency_code}")
        # Output: $29.99 USD
    """
    amount: float
    currency_code: str


class Product(BaseModel):
    """Product information returned to AI agents from search operations.
    
    Contains essential product details needed for display and cart creation.
    This is a simplified view focused on the most important fields for AI agent
    interactions, excluding internal fields like variants and price ranges.
    
    Attributes:
        id (str): Unique product identifier used for cart operations.
            Format is platform-specific (e.g., "gid://shopify/Product/123").
            This ID must be passed to create_shopping_cart to add items.
        title (str): Product name/title displayed to users.
            Human-readable product name (e.g., "Men's Running Shoes").
        description (str): Detailed product description.
            May contain HTML formatting. Provides full product details,
            features, materials, sizing information, etc.
        price (Price): Current product price.
            The base or default price for the product. Some products may have
            variant-specific pricing not reflected here.
        image_url (str): URL to the product's primary image.
            Can be displayed to users or used in rich UI responses.
            Typically a full HTTPS URL to a hosted image.
    
    Example:
        >>> product = Product(
        ...     id="gid://shopify/Product/789",
        ...     title="Wireless Headphones",
        ...     description="<p>Premium noise-cancelling headphones</p>",
        ...     price=Price(amount=149.99, currency_code="USD"),
        ...     image_url="https://cdn.example.com/headphones.jpg"
        ... )
    
    Note:
        - The id field must be used when creating carts with this product
        - HTML in description should be stripped or rendered appropriately
        - image_url may require authentication or have expiry times
    """
    id: str
    title: str
    description: str
    price: Price
    image_url: str


class ProductList(BaseModel):
    """Container for product search results.
    
    Simple wrapper around a list of products, returned by the search_products tool.
    Using a container model allows for future extension (e.g., adding pagination,
    result count, or search metadata) without breaking the existing interface.
    
    Attributes:
        products (list[Product]): List of products matching the search query.
            Defaults to empty list if no products found. List order typically
            reflects relevance or specified sort order.
    
    Example:
        >>> # Empty result
        >>> no_results = ProductList()  # products=[]
        >>> 
        >>> # Search results
        >>> results = ProductList(
        ...     products=[
        ...         Product(id="1", title="Item 1", ...),
        ...         Product(id="2", title="Item 2", ...),
        ...         Product(id="3", title="Item 3", ...)
        ...     ]
        ... )
        >>> print(f"Found {len(results.products)} products")
    """
    products: list[Product] = Field(default_factory=list)


class Cart(BaseModel):
    """Shopping cart summary with pricing and checkout information.
    
    Represents a cart created or retrieved by the MCP server. Contains the
    checkout URL and complete pricing breakdown but excludes line item details
    to keep the interface simple. AI agents can direct users to the checkout_url
    to complete their purchase.
    
    Attributes:
        checkout_url (str): Direct URL to complete the checkout process.
            A fully-qualified HTTPS URL that users can visit to review their
            cart and complete payment. The URL typically includes a unique
            cart token and does not require authentication.
        subtotal_amount (Price): Cart subtotal before taxes and shipping.
            Sum of all item prices × quantities, before additional charges.
        tax_amount (Price | None): Calculated tax amount for the cart.
            May be None if taxes haven't been calculated yet, are not applicable,
            or if the delivery address is not set. Tax calculation depends on
            delivery location and local tax regulations.
        total_amount (Price): Final total amount to be charged.
            Includes subtotal, taxes, shipping, and any discounts. This is
            the amount the customer will pay at checkout.
    
    Example:
        >>> cart = Cart(
        ...     checkout_url="https://store.myshopify.com/cart/abc123def456",
        ...     subtotal_amount=Price(amount=99.98, currency_code="USD"),
        ...     tax_amount=Price(amount=9.00, currency_code="USD"),
        ...     total_amount=Price(amount=108.98, currency_code="USD")
        ... )
        >>> 
        >>> # Cart without calculated tax
        >>> cart = Cart(
        ...     checkout_url="https://store.myshopify.com/cart/xyz789",
        ...     subtotal_amount=Price(amount=50.00, currency_code="USD"),
        ...     tax_amount=None,  # Tax not yet calculated
        ...     total_amount=Price(amount=50.00, currency_code="USD")
        ... )
    
    Note:
        - checkout_url should be presented to users as a clickable link
        - Carts may expire after a period of inactivity (typically 10-30 days)
        - Prices may change between cart creation and checkout completion
        - Line item details are not included; users see items at checkout URL
    """
    checkout_url: str
    subtotal_amount: Price
    tax_amount: Price | None = None
    total_amount: Price


