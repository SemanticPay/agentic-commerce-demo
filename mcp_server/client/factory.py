"""
Factory module for creating storefront client instances.

This module implements the Factory design pattern to instantiate the appropriate
StoreFrontClient implementation based on the specified e-commerce platform provider.
It provides a centralized way to create client instances without requiring direct
knowledge of concrete implementation classes.

The factory pattern allows for:
    - Easy addition of new e-commerce platform support
    - Centralized client configuration and initialization
    - Decoupling of client creation from client usage
    - Simplified dependency management

Functions:
    get_storefront_client: Factory function that returns the appropriate client instance.

Supported Providers:
    - SHOPIFY: Shopify Storefront API client

Example Usage:
    >>> from factory import get_storefront_client
    >>> from base_types import StoreProvider
    >>> 
    >>> # Create a Shopify client
    >>> client = get_storefront_client(
    ...     provider=StoreProvider.SHOPIFY,
    ...     store_url="https://mystore.myshopify.com/api/2025-10/graphql.json",
    ...     access_token="your_storefront_access_token"
    ... )
    >>> 
    >>> # Use the client (interface is platform-agnostic)
    >>> products = client.search_products(SearchProductsRequest(query="shoes"))
    >>> cart = client.cart_create(CartCreateRequest(lines=[...]))

Adding New Providers:
    To add support for a new e-commerce platform:
    
    1. Create a new client class implementing StoreFrontClient interface
    2. Add the provider to StoreProvider enum in base_types.py
    3. Add a new elif branch in get_storefront_client() function
    
    Example:
        >>> # In base_types.py
        >>> class StoreProvider(Enum):
        ...     SHOPIFY = "SHOPIFY"
        ...     WOOCOMMERCE = "WOOCOMMERCE"  # New provider
        >>> 
        >>> # In factory.py
        >>> def get_storefront_client(provider: StoreProvider, **provider_kwargs):
        ...     if provider == StoreProvider.SHOPIFY:
        ...         return ShopifyGraphQLClient(...)
        ...     elif provider == StoreProvider.WOOCOMMERCE:
        ...         return WooCommerceClient(...)  # New implementation
        ...     else:
        ...         raise ValueError(f"Unsupported store provider: {provider}")

See Also:
    - interface.py: Abstract StoreFrontClient interface definition
    - base_types.py: StoreProvider enum and data models
    - shopify.py: Shopify-specific client implementation
"""

from interface import StoreFrontClient
from shopify import ShopifyGraphQLClient
from base_types import StoreProvider


def get_storefront_client(provider: StoreProvider, **provider_kwargs) -> StoreFrontClient:
    """Create and return a storefront client instance for the specified provider.
    
    Factory function that instantiates the appropriate StoreFrontClient implementation
    based on the provider type. The function abstracts away the details of client
    instantiation, allowing callers to work with the StoreFrontClient interface
    without knowing about specific implementation classes.
    
    This function uses the Factory pattern to enable:
        - Runtime selection of client implementation
        - Provider-specific configuration through kwargs
        - Centralized validation and error handling
        - Easy extensibility for new providers
    
    Args:
        provider (StoreProvider): The e-commerce platform provider enum value.
            Determines which client implementation to instantiate.
            Currently supported: StoreProvider.SHOPIFY
        **provider_kwargs: Variable keyword arguments passed to the provider-specific
            client constructor. Different providers may require different arguments.
            
            For Shopify (StoreProvider.SHOPIFY):
                - store_url (str): Shopify Storefront API GraphQL endpoint URL.
                  Format: https://{shop}.myshopify.com/api/{version}/graphql.json
                  Defaults to empty string if not provided.
                - access_token (str | None): Storefront access token for authentication.
                  Required for most Shopify operations. Defaults to None.
    
    Returns:
        StoreFrontClient: An instance of a concrete StoreFrontClient implementation
            (e.g., ShopifyGraphQLClient) that implements the standard interface
            for product search, cart creation, and cart retrieval operations.
    
    Raises:
        ValueError: If the provider is not supported. This occurs when a provider
            enum value is passed that doesn't have a corresponding implementation
            in this factory function.
    
    Example:
        >>> from factory import get_storefront_client
        >>> from base_types import StoreProvider, SearchProductsRequest
        >>> 
        >>> # Create a Shopify client
        >>> client = get_storefront_client(
        ...     provider=StoreProvider.SHOPIFY,
        ...     store_url="https://mystore.myshopify.com/api/2025-10/graphql.json",
        ...     access_token="abc123..."
        ... )
        >>> 
        >>> # Use the client through the standard interface
        >>> response = client.search_products(
        ...     SearchProductsRequest(query="laptops", first=10)
        ... )
        >>> print(f"Found {len(response.products)} products")
        >>> 
        >>> # Create cart
        >>> cart_response = client.cart_create(CartCreateRequest(lines=[...]))
        >>> print(f"Cart ID: {cart_response.cart.id}")
    
    Example (Error handling):
        >>> try:
        ...     client = get_storefront_client(
        ...         provider=StoreProvider.WOOCOMMERCE,  # Not yet supported
        ...         api_url="https://example.com"
        ...     )
        ... except ValueError as e:
        ...     print(f"Error: {e}")
        ...     # Output: Error: Unsupported store provider: StoreProvider.WOOCOMMERCE
    
    Note:
        - The returned client implements the StoreFrontClient interface, ensuring
          consistent behavior across different e-commerce platforms
        - Provider-specific configuration is isolated to this factory function
        - Invalid or missing provider_kwargs may cause errors in the client constructor
        - Future providers (WooCommerce, Magento, etc.) can be added by extending
          the if-elif chain
    
    See Also:
        - StoreFrontClient: Abstract interface that all clients implement
        - ShopifyGraphQLClient: Current Shopify implementation
        - StoreProvider: Enum defining available providers
    """
    if provider == StoreProvider.SHOPIFY:
        return ShopifyGraphQLClient(
            store_url=provider_kwargs.get("store_url", ""),
            access_token=provider_kwargs.get("access_token"),
        )
    else:
        raise ValueError(f"Unsupported store provider: {provider}")
