"""
Base type definitions for e-commerce storefront API clients.

This module contains Pydantic models representing core entities in e-commerce systems,
including products, carts, pricing, and user information. These models are designed to
be platform-agnostic and work across different e-commerce providers (Shopify, WooCommerce,
Magento, etc.). All models support both snake_case (Python) and camelCase (API) field
naming through Pydantic aliases for maximum compatibility.

Data Models:
    Core Entities:
        - StoreProvider: Enum of supported e-commerce platforms.
        - Price: Represents a monetary value with currency code.
        - PriceRange: Min/max price range across product variants.
        - ProductVariant: A specific variant of a product (e.g., size, color).
        - Product: Complete product information including variants and pricing.
        - SortKey: Enumeration of product sorting options.
    
    Cart & Customer:
        - CartLineInput: Input model for adding line items to cart.
        - BuyerIdentity: Customer identification (email, phone).
        - Address: Physical mailing/shipping address.
        - CartAddressInput: Wrapper for delivery address.
        - AddressOption: Delivery address option with selection status.
        - CartDeliveryInput: Container for delivery configuration.
        - Cost: Financial breakdown of cart costs (subtotal, tax, total).
        - Cart: Shopping cart with items and checkout information.
    
    API Communication:
        - UserError: User-facing error message with field context.
        - CartWarning: Non-fatal warning message for cart operations.
        - SearchProductsRequest: Parameters for product search queries.
        - SearchProductsResponse: Product search results.
        - CartGetRequest: Request to retrieve existing cart by ID.
        - CartGetResponse: Response containing retrieved cart data.
        - CartCreateRequest: Request to create a new shopping cart.
        - CartCreateResponse: Response from cart creation with errors/warnings.

Field Naming:
    All models support dual naming conventions for API compatibility:
    - Python convention: snake_case (e.g., buyer_identity, total_amount)
    - API convention: camelCase (e.g., buyerIdentity, totalAmount)
    
    This is achieved through Pydantic's Field aliases, allowing seamless
    serialization/deserialization with various e-commerce platform APIs.

Example:
    >>> # Create a product with either naming convention
    >>> product = Product(
    ...     id="123",
    ...     title="T-Shirt",
    ...     description="Cotton t-shirt",
    ...     images=["https://example.com/img.jpg"],
    ...     price=Price(amount=19.99, currency_code="USD"),
    ...     price_range=PriceRange(...)  # Using snake_case
    ... )
    >>> # Or using API naming
    >>> product = Product(
    ...     id="123",
    ...     title="T-Shirt",
    ...     description="Cotton t-shirt",
    ...     images=["https://example.com/img.jpg"],
    ...     price=Price(amount=19.99, currencyCode="USD"),
    ...     priceRange=PriceRange(...)  # Using camelCase
    ... )

See Also:
    - interface.py: Abstract StoreFrontClient interface
    - factory.py: Factory for creating provider-specific clients
    - shopify.py: Shopify-specific implementation
"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class StoreProvider(Enum):
    """Represents a specific store provider.
    
    Options:
        - SHOPIFY
    """
    SHOPIFY = "SHOPIFY"


class Price(BaseModel):
    """Represents a monetary value with its currency.
    
    Used throughout the API to represent prices, costs, and financial amounts.
    
    Attributes:
        amount (float): The numeric price value (e.g., 19.99).
        currency_code (str): ISO 4217 currency code (e.g., "USD", "EUR", "GBP").
            Maps to "currencyCode" in API responses.
    
    Example:
        >>> price = Price(amount=29.99, currency_code="USD")
        >>> price = Price(amount=29.99, currencyCode="USD")  # Using alias
    """
    amount: float
    currency_code: str = Field(alias="currencyCode")


class PriceRange(BaseModel):
    """Represents the price range across all variants of a product.
    
    Useful for displaying price ranges like "$10.00 - $25.00" when a product
    has multiple variants at different price points.
    
    Attributes:
        min_variant_price (Price): The lowest price among all product variants.
            Maps to "minVariantPrice" in API responses.
        max_variant_price (Price): The highest price among all product variants.
            Maps to "maxVariantPrice" in API responses.
    
    Example:
        >>> price_range = PriceRange(
        ...     minVariantPrice=Price(amount=10.00, currencyCode="USD"),
        ...     maxVariantPrice=Price(amount=25.00, currencyCode="USD")
        ... )
    """
    min_variant_price: Price = Field(alias="minVariantPrice")
    max_variant_price: Price = Field(alias="maxVariantPrice")


class ProductVariant(BaseModel):
    """Represents a specific variant of a product.
    
    Products can have multiple variants representing different options like size,
    color, material, etc. Each variant has its own ID, title, and price.
    
    Attributes:
        id (str): Unique identifier for this variant (e.g., "gid://shopify/ProductVariant/123").
        title (str): Display name for this variant (e.g., "Small / Red", "Large").
        price (Price): The price specific to this variant.
    
    Example:
        >>> variant = ProductVariant(
        ...     id="gid://shopify/ProductVariant/123",
        ...     title="Medium / Blue",
        ...     price=Price(amount=19.99, currencyCode="USD")
        ... )
    """
    id: str
    title: str
    price: Price


class Product(BaseModel):
    """Represents a complete product with all its details.
    
    The main product entity containing all information needed to display
    and purchase an item, including variants, images, and pricing information.
    
    Attributes:
        id (str): Unique product identifier (e.g., "gid://shopify/Product/123").
        title (str): Product name/title displayed to customers.
        description (str): Detailed product description (may contain HTML).
        images (list[str]): List of image URLs for product photos.
        price (Price): Base/default price for the product.
        price_range (PriceRange | None): Optional price range if product has variants
            with different prices. Maps to "priceRange" in API responses.
        variants (list[ProductVariant]): List of product variants.
    
    Example:
        >>> product = Product(
        ...     id="gid://shopify/Product/123",
        ...     title="Cotton T-Shirt",
        ...     description="Comfortable 100% cotton t-shirt",
        ...     images=["https://example.com/image1.jpg"],
        ...     price=Price(amount=19.99, currencyCode="USD"),
        ...     priceRange=PriceRange(...),
        ...     variants=[ProductVariant(...)]
        ... )
    """
    id: str
    title: str
    description: str
    images: list[str]
    price: Price
    price_range: PriceRange | None = Field(default=None, alias="priceRange")
    variants: list[ProductVariant]


class SortKey(Enum):
    """Enumeration of available product sorting options.
    
    Defines the available sort keys for product search queries.
    
    Attributes:
        RELEVANCE: Sort by search relevance (best match for query).
    
    Note:
        Additional sort keys like TITLE, PRICE, CREATED_AT may be supported
        by the API but are not currently defined in this enum.
    """
    RELEVANCE = "RELEVANCE"


class CartLineInput(BaseModel):
    """Input model for adding a product line item to a shopping cart.
    
    Represents a single item to be added to the cart, including the product
    variant and desired quantity.
    
    Attributes:
        quantity (int): Number of units to add (must be positive).
        merchandise_id (str): The variant ID to add to cart
            (e.g., "gid://shopify/ProductVariant/123").
            Maps to "merchandiseId" in API requests.
    
    Config:
        Validates using both Python field names (snake_case) and API aliases (camelCase).
    
    Example:
        >>> cart_line = CartLineInput(
        ...     quantity=2,
        ...     merchandiseId="gid://shopify/ProductVariant/123"
        ... )
    """
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    quantity: int
    merchandise_id: str = Field(alias="merchandiseId")


class BuyerIdentity(BaseModel):
    """Customer identification and contact information.
    
    Used to associate a cart with a specific customer and provide contact
    information for order fulfillment and communication.
    
    Attributes:
        email (str | None): Customer's email address. Optional but recommended
            for order confirmation and communication.
        phone (str | None): Customer's phone number. Optional, useful for
            delivery notifications and support.
    
    Config:
        Validates using both Python field names (snake_case) and API aliases (camelCase).
    
    Example:
        >>> buyer = BuyerIdentity(
        ...     email="customer@example.com",
        ...     phone="+1234567890"
        ... )
    """
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    email: str | None = None
    phone: str | None = None


class Address(BaseModel):
    """Physical mailing/shipping address information.
    
    Comprehensive address model supporting international addresses with all
    common fields needed for shipping and billing.
    
    Attributes:
        address1 (str | None): Primary street address line (e.g., "123 Main St").
        address2 (str | None): Secondary address line (e.g., "Apt 4B", "Suite 200").
        city (str | None): City or locality name.
        country_code (str | None): ISO 3166-1 alpha-2 country code (e.g., "US", "CA", "GB").
            Maps to "countryCode" in API requests.
        zip (str | None): Postal/ZIP code.
        phone (str | None): Contact phone number for this address.
        first_name (str | None): Recipient's first name.
            Maps to "firstName" in API requests.
        last_name (str | None): Recipient's last name.
            Maps to "lastName" in API requests.
    
    Config:
        Validates using both Python field names (snake_case) and API aliases (camelCase).
    
    Example:
        >>> address = Address(
        ...     address1="123 Main Street",
        ...     address2="Apt 4B",
        ...     city="New York",
        ...     countryCode="US",
        ...     zip="10001",
        ...     phone="+12125551234",
        ...     firstName="John",
        ...     lastName="Doe"
        ... )
    """
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
    """Wrapper for delivery address in cart operations.
    
    Wraps an Address object in the format expected by Shopify's cart API,
    which requires the address to be nested under a "deliveryAddress" field.
    
    Attributes:
        delivery_address (Address): The delivery address for cart items.
            Maps to "deliveryAddress" in API requests.
    
    Config:
        Validates using both Python field names (snake_case) and API aliases (camelCase).
    
    Example:
        >>> cart_address = CartAddressInput(
        ...     deliveryAddress=Address(
        ...         address1="123 Main St",
        ...         city="New York",
        ...         countryCode="US",
        ...         zip="10001"
        ...     )
        ... )
    
    Note:
        This is a wrapper class to match Shopify's API structure where the
        address must be nested under the "deliveryAddress" key.
    """
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
    delivery_address: Address = Field(alias="deliveryAddress")


class AddressOption(BaseModel):
    """Represents a delivery address option with selection status.
    
    Used when multiple delivery addresses are available, allowing the customer
    to choose their preferred delivery location.
    
    Attributes:
        address (CartAddressInput): A delivery address option.
        selected (bool): Whether this address is currently selected as the
            preferred delivery address.
    
    Example:
        >>> address_option = AddressOption(
        ...     address=CartAddressInput(deliveryAddress=Address(...)),
        ...     selected=True
        ... )
    """
    address: CartAddressInput
    selected: bool


class CartDeliveryInput(BaseModel):
    """Container for delivery configuration in cart operations.
    
    Holds all delivery-related information for a cart, including one or more
    possible delivery addresses.
    
    Attributes:
        addresses (list[AddressOption] | None): Optional list of delivery address
            options. Each option includes an address and whether it's selected.
            If None or empty, no specific delivery address is set.
    
    Example:
        >>> delivery = CartDeliveryInput(
        ...     addresses=[
        ...         AddressOption(
        ...             address=CartAddressInput(deliveryAddress=Address(...)),
        ...             selected=True
        ...         )
        ...     ]
        ... )
    """
    addresses: list[AddressOption] | None = None


class UserError(BaseModel):
    """Represents a user-facing error from the API.
    
    Contains information about validation or business logic errors that should
    be displayed to the user, often associated with specific input fields.
    
    Attributes:
        field (list[str] | None): Optional list of field paths that caused the error.
            For example, ["input", "email"] indicates the error is related to
            the email field in the input. None if error is not field-specific.
        message (str): Human-readable error message describing what went wrong.
            Should be suitable for displaying to end users.
    
    Example:
        >>> error = UserError(
        ...     field=["input", "buyerIdentity", "email"],
        ...     message="Email address is invalid"
        ... )
        >>> general_error = UserError(
        ...     field=None,
        ...     message="Unable to process request"
        ... )
    """
    field: list[str] | None = None
    message: str


class CartWarning(BaseModel):
    """Represents a warning message about cart operations.
    
    Warnings are non-fatal issues that don't prevent the operation from
    completing but inform the user about potential concerns or limitations.
    
    Attributes:
        message (str): Human-readable warning message. Should be suitable for
            displaying to end users. Examples include inventory warnings,
            shipping restrictions, or promotional limitations.
    
    Example:
        >>> warning = CartWarning(
        ...     message="Some items have limited availability"
        ... )
    """
    message: str


class Cost(BaseModel):
    """Financial breakdown of cart costs.
    
    Provides detailed pricing information for a shopping cart, including
    subtotals, taxes, and the final total amount.
    
    Attributes:
        subtotal_amount (Price): Cart subtotal before taxes and discounts.
            Maps to "subtotalAmount" in API responses.
        total_tax_amount (Price | None): Total tax amount calculated for the cart.
            May be None if taxes haven't been calculated yet or are not applicable.
            Maps to "totalTaxAmount" in API responses.
        total_amount (Price): Final total amount including all charges.
            Maps to "totalAmount" in API responses.
    
    Example:
        >>> cost = Cost(
        ...     subtotalAmount=Price(amount=50.00, currencyCode="USD"),
        ...     totalTaxAmount=Price(amount=4.50, currencyCode="USD"),
        ...     totalAmount=Price(amount=54.50, currencyCode="USD")
        ... )
    """
    subtotal_amount: Price = Field(alias="subtotalAmount")
    total_tax_amount: Price | None = Field(default=None, alias="totalTaxAmount")
    total_amount: Price = Field(alias="totalAmount")


class Cart(BaseModel):
    """Represents a shopping cart with items and checkout information.
    
    The main cart entity containing all information about the customer's
    current shopping session, including items, quantities, costs, and
    the URL to proceed to checkout.
    
    Attributes:
        id (str): Unique cart identifier (e.g., "gid://shopify/Cart/abc123").
            Used for retrieving and updating the cart.
        checkout_url (str): Direct URL to the checkout page for this cart.
            Maps to "checkoutUrl" in API responses.
        total_quantity (int): Total number of items in the cart across all line items.
            Maps to "totalQuantity" in API responses.
        cost (Cost): Detailed cost breakdown including subtotal, tax, and total.
    
    Example:
        >>> cart = Cart(
        ...     id="gid://shopify/Cart/abc123",
        ...     checkoutUrl="https://store.myshopify.com/cart/abc123",
        ...     totalQuantity=3,
        ...     cost=Cost(...)
        ... )
    """
    id: str
    checkout_url: str = Field(alias="checkoutUrl")
    total_quantity: int = Field(alias="totalQuantity")
    cost: Cost


# ============================================================================
# Search Operations
# ============================================================================


class SearchProductsRequest(BaseModel):
    """Request model for searching products in the store.
    
    Defines all parameters for executing a product search query, including
    search terms, pagination, and sorting options.
    
    Attributes:
        query (str): Search query string to match against product titles,
            descriptions, tags, etc. Examples: "shoes", "red dress", "nike running".
            Defaults to empty string (returns all products).
        first (int): Maximum number of products to return in the results.
            Must be between 1 and 250. Defaults to 10.
        sort_key (str): Field to sort results by. Defaults to SortKey.RELEVANCE.value.
            Other possible values include "TITLE", "PRICE", "CREATED_AT", "UPDATED_AT",
            "BEST_SELLING", "PRODUCT_TYPE", "VENDOR".
        reverse (bool): Whether to reverse the sort order. When False, sorts ascending
            (A-Z, oldest first, lowest price first). When True, sorts descending
            (Z-A, newest first, highest price first). Defaults to False.
    
    Example:
        >>> # Search for shoes, get top 20 results by relevance
        >>> request = SearchProductsRequest(
        ...     query="running shoes",
        ...     first=20,
        ...     sort_key="RELEVANCE",
        ...     reverse=False
        ... )
        >>> 
        >>> # Get newest products
        >>> request = SearchProductsRequest(
        ...     query="",
        ...     first=50,
        ...     sort_key="CREATED_AT",
        ...     reverse=True
        ... )
    """
    query: str = ""
    first: int = 10
    sort_key: str = SortKey.RELEVANCE.value
    reverse: bool = False


class SearchProductsResponse(BaseModel):
    """Response model containing product search results.
    
    Returns a list of products that match the search criteria from a
    SearchProductsRequest.
    
    Attributes:
        products (list[Product]): List of products matching the search query.
            May be empty if no products match. Length is limited by the 'first'
            parameter in the request.
    
    Example:
        >>> response = SearchProductsResponse(
        ...     products=[
        ...         Product(id="1", title="Running Shoes", ...),
        ...         Product(id="2", title="Walking Shoes", ...)
        ...     ]
        ... )
    """
    products: list[Product]


# ============================================================================
# Cart Get Operations
# ============================================================================


class CartGetRequest(BaseModel):
    """Request model for retrieving an existing cart.
    
    Simple request containing only the cart ID needed to fetch cart details.
    
    Attributes:
        id (str): The unique cart identifier (e.g., "gid://shopify/Cart/abc123").
            This is the ID returned when the cart was created.
    
    Example:
        >>> request = CartGetRequest(id="gid://shopify/Cart/abc123")
    """
    id: str


class CartGetResponse(BaseModel):
    """Response model containing the retrieved cart data.
    
    Simple response wrapper containing the full cart object.
    
    Attributes:
        cart (Cart): The complete cart object with all items, costs, and checkout URL.
    
    Example:
        >>> response = CartGetResponse(
        ...     cart=Cart(
        ...         id="gid://shopify/Cart/abc123",
        ...         checkoutUrl="https://...",
        ...         totalQuantity=2,
        ...         cost=Cost(...)
        ...     )
        ... )
    """
    cart: Cart


# ============================================================================
# Cart Create Operations
# ============================================================================


class CartCreateRequest(BaseModel):
    """Request model for creating a new shopping cart.
    
    Contains all information needed to initialize a new cart, including
    initial items, customer information, and delivery preferences.
    
    Attributes:
        lines (list[CartLineInput] | None): Optional list of initial items to add
            to the cart. Each line item specifies a product variant and quantity.
            Can be None to create an empty cart.
        buyer_identity (BuyerIdentity | None): Optional customer identification
            information (email, phone). Maps to "buyerIdentity" in API requests.
            Useful for associating the cart with a known customer.
        delivery (CartDeliveryInput | None): Optional delivery configuration
            including delivery addresses. Can be set later if not provided initially.
    
    Example:
        >>> # Create cart with items and customer info
        >>> request = CartCreateRequest(
        ...     lines=[
        ...         CartLineInput(
        ...             quantity=2,
        ...             merchandiseId="gid://shopify/ProductVariant/123"
        ...         )
        ...     ],
        ...     buyerIdentity=BuyerIdentity(
        ...         email="customer@example.com",
        ...         phone="+1234567890"
        ...     ),
        ...     delivery=CartDeliveryInput(
        ...         addresses=[AddressOption(...)]
        ...     )
        ... )
        >>> 
        >>> # Create empty cart
        >>> request = CartCreateRequest()
    """
    lines: list[CartLineInput] | None = None
    buyer_identity: BuyerIdentity | None = Field(default=None, alias="buyerIdentity")
    delivery: CartDeliveryInput | None = None


class CartCreateResponse(BaseModel):
    """Response model from cart creation operation.
    
    Contains the newly created cart along with any errors or warnings
    that occurred during creation.
    
    Attributes:
        cart (Cart): The newly created cart object with generated ID and checkout URL.
        user_errors (list[UserError]): List of validation or business logic errors
            that occurred. Maps to "userErrors" in API responses. Defaults to empty list.
            If not empty, the cart may not have been created successfully.
        warnings (list[CartWarning]): List of non-fatal warnings about the cart
            creation. Defaults to empty list. Cart is still created even if warnings
            are present.
    
    Example:
        >>> # Successful creation
        >>> response = CartCreateResponse(
        ...     cart=Cart(
        ...         id="gid://shopify/Cart/abc123",
        ...         checkoutUrl="https://...",
        ...         totalQuantity=2,
        ...         cost=Cost(...)
        ...     ),
        ...     userErrors=[],
        ...     warnings=[]
        ... )
        >>> 
        >>> # Creation with errors
        >>> response = CartCreateResponse(
        ...     cart=Cart(...),
        ...     userErrors=[
        ...         UserError(
        ...             field=["input", "lines", "0", "merchandiseId"],
        ...             message="Variant not found"
        ...         )
        ...     ],
        ...     warnings=[]
        ... )
    """
    cart: Cart
    user_errors: list[UserError] = Field(default=[], alias="userErrors")
    warnings: list[CartWarning] = Field(default=[])
