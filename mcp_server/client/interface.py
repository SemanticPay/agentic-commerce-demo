"""
Abstract interface for e-commerce storefront clients.

This module defines the contract that all storefront client implementations must follow.
It provides a standardized interface for interacting with different e-commerce platforms
(Shopify, WooCommerce, Magento, etc.) through a common API, enabling the MCP server to
support multiple backends without changing the tool implementations.

The interface uses the Strategy pattern to allow runtime selection of e-commerce
platform implementations while maintaining a consistent API surface.

Classes:
    StoreFrontClient: Abstract base class defining the storefront client interface.

Design Pattern:
    This module implements the Strategy pattern where:
    - StoreFrontClient is the strategy interface
    - Concrete implementations (ShopifyGraphQLClient, etc.) are strategy classes
    - The factory module selects which strategy to instantiate
    - The MCP server (main.py) is the context that uses the strategy

Benefits:
    - Platform Independence: MCP tools work with any e-commerce platform
    - Extensibility: Add new platforms without modifying existing code
    - Type Safety: All implementations must conform to typed contracts
    - Testability: Easy to mock for testing by implementing the interface

Usage:
    To implement a new storefront client, inherit from StoreFrontClient and implement
    all abstract methods:
    
    >>> from mcp_server.client.interface import StoreFrontClient
    >>> from mcp_server.client.base_types import *
    >>> 
    >>> class MyStoreFrontClient(StoreFrontClient):
    ...     def __init__(self, api_url: str, api_key: str):
    ...         self.api_url = api_url
    ...         self.api_key = api_key
    ...     
    ...     def search_products(self, req: SearchProductsRequest) -> SearchProductsResponse:
    ...         # Call your platform's product search API
    ...         # Transform response to SearchProductsResponse
    ...         pass
    ...     
    ...     def cart_create(self, req: CartCreateRequest) -> CartCreateResponse:
    ...         # Call your platform's cart creation API
    ...         # Transform response to CartCreateResponse
    ...         pass
    ...     
    ...     def cart_get(self, req: CartGetRequest) -> CartGetResponse:
    ...         # Call your platform's cart retrieval API
    ...         # Transform response to CartGetResponse
    ...         pass

Integration Steps:
    1. Create new client class implementing StoreFrontClient
    2. Add provider to StoreProvider enum in base_types.py
    3. Register in factory.py's get_storefront_client function
    4. Update main.py configuration to use new provider

See Also:
    - base_types.py: Type definitions for requests/responses
    - factory.py: Factory function for creating client instances
    - shopify.py: Example implementation for Shopify
"""

from abc import ABC, abstractmethod

# Support both relative imports (when imported as module) and absolute imports (when run directly)
try:
    from .base_types import CartCreateResponse, CartCreateRequest, CartGetRequest, CartGetResponse, SearchProductsRequest, SearchProductsResponse
except ImportError:
    from base_types import CartCreateResponse, CartCreateRequest, CartGetRequest, CartGetResponse, SearchProductsRequest, SearchProductsResponse


class StoreFrontClient(ABC):
    """Abstract base class for e-commerce storefront client implementations.
    
    This class defines the contract that all storefront clients must implement,
    providing a unified interface for product search and shopping cart operations
    across different e-commerce platforms.
    
    All methods in this interface use strongly-typed request and response models
    from the base_types module, ensuring type safety and consistent data structures.
    
    Implementations should handle platform-specific API calls, authentication,
    error handling, and data transformation to conform to the standard models.
    
    Methods:
        search_products: Search for products using various criteria.
        cart_create: Create a new shopping cart with optional initial items.
        cart_get: Retrieve an existing cart by its unique identifier.
    
    Example:
        >>> class ShopifyClient(StoreFrontClient):
        ...     def __init__(self, store_url: str, access_token: str):
        ...         self.store_url = store_url
        ...         self.access_token = access_token
        ...     
        ...     def search_products(self, req: SearchProductsRequest) -> SearchProductsResponse:
        ...         # Make Shopify API call
        ...         response = self._call_shopify_api(req)
        ...         return SearchProductsResponse(products=response)
        ...     
        ...     # Implement other methods...
    
    Note:
        This is an abstract class and cannot be instantiated directly.
        All subclasses must implement all abstract methods.
    """
    
    @abstractmethod
    def search_products(
        self,
        req: SearchProductsRequest
    ) -> SearchProductsResponse:
        """Search for products in the storefront using flexible criteria.
        
        Executes a product search against the e-commerce platform's product catalog,
        supporting text queries, sorting, and pagination. The implementation should
        translate the standard request format into platform-specific API calls.
        
        Args:
            req (SearchProductsRequest): Search request containing:
                - query (str): Search text to match against product titles, descriptions,
                  tags, and other searchable fields. Empty string returns all products.
                - first (int): Maximum number of products to return (pagination limit).
                - sort_key (str): Field to sort by (e.g., "RELEVANCE", "PRICE", "TITLE").
                - reverse (bool): Whether to reverse the sort order.
        
        Returns:
            SearchProductsResponse: Response containing:
                - products (list[Product]): List of matching products with full details
                  including ID, title, description, images, price, and variants.
        
        Raises:
            NotImplementedError: If the method is not implemented by subclass.
            ConnectionError: If unable to connect to the storefront API.
            AuthenticationError: If API credentials are invalid or expired.
            ValueError: If request parameters are invalid.
        
        Example:
            >>> client = MyStoreFrontClient()
            >>> request = SearchProductsRequest(
            ...     query="running shoes",
            ...     first=20,
            ...     sort_key="RELEVANCE",
            ...     reverse=False
            ... )
            >>> response = client.search_products(request)
            >>> print(f"Found {len(response.products)} products")
            >>> for product in response.products:
            ...     print(f"- {product.title}: ${product.price.amount}")
        
        Note:
            - Search behavior (exact match vs. fuzzy search) depends on the platform.
            - Some platforms may have limits on the maximum 'first' value.
            - Results may be cached by the platform for performance.
        """
        pass

    @abstractmethod
    def cart_create(self, req: CartCreateRequest) -> CartCreateResponse:
        """Create a new shopping cart in the storefront.
        
        Initializes a new cart session on the e-commerce platform, optionally adding
        initial line items, associating a customer, and setting delivery preferences.
        The implementation should handle platform-specific cart creation and return
        a standardized response.
        
        Args:
            req (CartCreateRequest): Cart creation request containing:
                - lines (list[CartLineInput] | None): Optional list of initial items
                  to add. Each item includes a product variant ID and quantity.
                  None or empty list creates an empty cart.
                - buyer_identity (BuyerIdentity | None): Optional customer information
                  including email and phone for order communication and tracking.
                - delivery (CartDeliveryInput | None): Optional delivery configuration
                  with one or more address options for shipping.
        
        Returns:
            CartCreateResponse: Response containing:
                - cart (Cart): The newly created cart with generated ID, checkout URL,
                  total quantity, and cost breakdown.
                - user_errors (list[UserError]): List of validation or business logic
                  errors encountered. Non-empty indicates cart may not be valid.
                - warnings (list[CartWarning]): List of non-fatal warnings (e.g.,
                  inventory limitations, shipping restrictions).
        
        Raises:
            NotImplementedError: If the method is not implemented by subclass.
            ConnectionError: If unable to connect to the storefront API.
            AuthenticationError: If API credentials are invalid or expired.
            ValueError: If request contains invalid product IDs or quantities.
        
        Example:
            >>> client = MyStoreFrontClient()
            >>> request = CartCreateRequest(
            ...     lines=[
            ...         CartLineInput(
            ...             quantity=2,
            ...             merchandiseId="gid://shopify/ProductVariant/123"
            ...         ),
            ...         CartLineInput(
            ...             quantity=1,
            ...             merchandiseId="gid://shopify/ProductVariant/456"
            ...         )
            ...     ],
            ...     buyerIdentity=BuyerIdentity(
            ...         email="customer@example.com",
            ...         phone="+1234567890"
            ...     )
            ... )
            >>> response = client.cart_create(request)
            >>> 
            >>> if response.user_errors:
            ...     print("Errors:", [e.message for e in response.user_errors])
            >>> else:
            ...     print(f"Cart created: {response.cart.id}")
            ...     print(f"Checkout URL: {response.cart.checkout_url}")
            ...     print(f"Total: ${response.cart.cost.total_amount.amount}")
        
        Note:
            - Cart IDs are typically temporary and may expire after a period of inactivity.
            - Some platforms require at least one item in the cart at creation time.
            - Prices and availability are validated at creation time; items may become
              unavailable or change price before checkout is completed.
        """
        pass

    @abstractmethod
    def cart_get(self, req: CartGetRequest) -> CartGetResponse:
        """Retrieve an existing shopping cart by its unique identifier.
        
        Fetches the current state of a previously created cart from the e-commerce
        platform, including all items, quantities, pricing, and checkout information.
        This is useful for resuming a shopping session or checking cart status.
        
        Args:
            req (CartGetRequest): Cart retrieval request containing:
                - id (str): The unique cart identifier returned from cart_create.
                  Format is platform-specific (e.g., "gid://shopify/Cart/abc123").
        
        Returns:
            CartGetResponse: Response containing:
                - cart (Cart): The complete cart object with:
                    - id (str): The cart's unique identifier.
                    - checkout_url (str): Direct URL to proceed to checkout.
                    - total_quantity (int): Total number of items across all line items.
                    - cost (Cost): Current cost breakdown including subtotal, tax, and total.
        
        Raises:
            NotImplementedError: If the method is not implemented by subclass.
            ConnectionError: If unable to connect to the storefront API.
            AuthenticationError: If API credentials are invalid or expired.
            ValueError: If cart ID format is invalid.
            LookupError: If the cart ID does not exist or has expired.
        
        Example:
            >>> client = MyStoreFrontClient()
            >>> 
            >>> # Create a cart first
            >>> create_response = client.cart_create(CartCreateRequest(...))
            >>> cart_id = create_response.cart.id
            >>> 
            >>> # Later, retrieve the cart
            >>> request = CartGetRequest(id=cart_id)
            >>> response = client.cart_get(request)
            >>> 
            >>> print(f"Cart {response.cart.id}")
            >>> print(f"Total items: {response.cart.total_quantity}")
            >>> print(f"Total cost: ${response.cart.cost.total_amount.amount}")
            >>> print(f"Checkout: {response.cart.checkout_url}")
        
        Note:
            - Carts may expire after a period of inactivity (typically 10-30 days).
            - Prices and availability may change between cart creation and retrieval.
            - Some platforms may update cart contents automatically (e.g., removing
              out-of-stock items or applying price changes).
            - The checkout URL is typically a deep link that can be shared or bookmarked.
        """
        pass
