"""
Shopify Storefront API client implementation.

This module provides a concrete implementation of the StoreFrontClient interface
for interacting with Shopify stores via the Shopify Storefront GraphQL API.
It handles product search, cart creation, and cart retrieval operations.

The client uses GraphQL queries and mutations to communicate with Shopify's
Storefront API, which is designed for customer-facing operations (as opposed
to the Admin API for backend operations).

Classes:
    ShopifyGraphQLClient: Shopify-specific implementation of StoreFrontClient.

Key Features:
    - Product search with flexible filtering, sorting, and pagination
    - Shopping cart creation with line items, buyer info, and delivery addresses
    - Cart retrieval by ID for session resumption
    - Automatic data transformation between Shopify and standard formats
    - Error handling for API failures and validation errors

Authentication:
    The Storefront API requires a Storefront Access Token, which can be generated
    in the Shopify admin panel under Apps > Manage private apps or through the
    Shopify Partners dashboard for custom apps.

API Version:
    This client targets Shopify Storefront API version 2025-10. Different versions
    may have different field availability or behavior.

Example Usage:
    >>> from shopify import ShopifyGraphQLClient
    >>> from base_types import SearchProductsRequest, CartCreateRequest, CartLineInput
    >>> 
    >>> # Initialize client
    >>> client = ShopifyGraphQLClient(
    ...     store_url="https://mystore.myshopify.com/api/2025-10/graphql.json",
    ...     access_token="your_storefront_access_token"
    ... )
    >>> 
    >>> # Search for products
    >>> response = client.search_products(SearchProductsRequest(query="shoes", first=10))
    >>> print(f"Found {len(response.products)} products")
    >>> 
    >>> # Create a cart
    >>> cart_response = client.cart_create(CartCreateRequest(lines=[...]))
    >>> print(f"Cart ID: {cart_response.cart.id}")

See Also:
    - Shopify Storefront API documentation: https://shopify.dev/api/storefront
    - GraphQL API reference: https://shopify.dev/api/storefront/reference
"""

import requests
from typing import Dict, Any, Optional

# Support both relative imports (when imported as module) and absolute imports (when run directly)
try:
    from .base_types import BuyerIdentity, CartGetRequest, CartGetResponse, Product, SearchProductsRequest, SearchProductsResponse, CartCreateRequest, CartCreateResponse, Cart, CartLineInput, Address, AddressOption, CartAddressInput, CartDeliveryInput
    from .interface import StoreFrontClient
except ImportError:
    from base_types import BuyerIdentity, CartGetRequest, CartGetResponse, Product, SearchProductsRequest, SearchProductsResponse, CartCreateRequest, CartCreateResponse, Cart, CartLineInput, Address, AddressOption, CartAddressInput, CartDeliveryInput
    from interface import StoreFrontClient


class ShopifyGraphQLClient(StoreFrontClient):
    """Shopify Storefront GraphQL API client implementation.
    
    Concrete implementation of the StoreFrontClient interface that communicates
    with Shopify stores using GraphQL queries and mutations. This client handles
    all Shopify-specific API details including authentication, query formatting,
    response parsing, and error handling.
    
    The client transforms between Shopify's GraphQL schema and the standardized
    models defined in base_types, providing a consistent interface regardless
    of the underlying e-commerce platform.
    
    Attributes:
        store_url (str): The complete Shopify Storefront API GraphQL endpoint URL.
        access_token (str | None): Storefront access token for authentication.
        headers (dict): HTTP headers used for all API requests, including auth.
    
    Methods:
        search_products: Search Shopify product catalog with filtering and sorting.
        cart_create: Create a new Shopify cart with items and customer info.
        cart_get: Retrieve existing cart by ID.
    
    Example:
        >>> # Initialize with store URL and access token
        >>> client = ShopifyGraphQLClient(
        ...     store_url="https://mystore.myshopify.com/api/2025-10/graphql.json",
        ...     access_token="abc123..."
        ... )
        >>> 
        >>> # Search for products
        >>> products = client.search_products(
        ...     SearchProductsRequest(query="shirts", first=20)
        ... )
        >>> 
        >>> # Create cart with first product's variant
        >>> if products.products and products.products[0].variants:
        ...     variant_id = products.products[0].variants[0].id
        ...     cart = client.cart_create(
        ...         CartCreateRequest(
        ...             lines=[CartLineInput(merchandiseId=variant_id, quantity=1)]
        ...         )
        ...     )
    
    Note:
        - Requires a valid Storefront Access Token from Shopify admin
        - API version is specified in the store_url (e.g., /api/2025-10/graphql.json)
        - Rate limits apply based on your Shopify plan
        - All times are in UTC
    """
    
    def __init__(self, store_url: str, access_token: Optional[str] = None):
        """Initialize the Shopify GraphQL client with store credentials.
        
        Sets up the client with the necessary configuration to communicate with
        a specific Shopify store's Storefront API endpoint.
        
        Args:
            store_url (str): The full Shopify Storefront API GraphQL endpoint URL.
                Format: https://{shop}.myshopify.com/api/{version}/graphql.json
                The version (e.g., 2025-10) determines available features and schema.
            access_token (str | None): Storefront access token for authentication.
                Required for most operations. Can be None for public/unauthenticated
                access if the store allows it. Generate in Shopify admin under
                Apps > Manage private apps or through Partners dashboard.
        
        Example:
            >>> # Initialize with custom store
            >>> client = ShopifyGraphQLClient(
            ...     store_url="https://myshop.myshopify.com/api/2025-10/graphql.json",
            ...     access_token="your_storefront_access_token_here"
            ... )
            >>> 
            >>> # Initialize with default store (for testing)
            >>> client = ShopifyGraphQLClient()
        
        Note:
            The access token should be a Storefront Access Token, not an Admin API
            token. These are different and have different permissions.
        """
        self.store_url = store_url
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
        }
        
        if access_token:
            self.headers["X-Shopify-Storefront-Access-Token"] = access_token
    
    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query or mutation against Shopify's Storefront API.
        
        Internal helper method that handles the HTTP communication with Shopify,
        including request formatting, error handling, and response parsing.
        
        Args:
            query (str): The GraphQL query or mutation string. Should be a valid
                GraphQL operation with properly formatted syntax.
            variables (dict[str, Any] | None): Optional dictionary of variables
                to pass to the GraphQL operation. Keys should match variable names
                defined in the query. Defaults to empty dict if None.
        
        Returns:
            dict[str, Any]: The "data" portion of the GraphQL response, parsed
                from JSON. Contains the requested fields as nested dictionaries.
        
        Raises:
            requests.HTTPError: If the HTTP request fails (status code 4xx or 5xx).
                Includes network errors, authentication failures, rate limiting, etc.
            Exception: If the GraphQL response contains errors in the "errors" field.
                This indicates query syntax errors, field errors, or business logic
                validation failures.
            requests.Timeout: If the request takes longer than 30 seconds.
        
        Example:
            >>> query = '''
            ... query getProduct($id: ID!) {
            ...     product(id: $id) {
            ...         title
            ...         price { amount currencyCode }
            ...     }
            ... }
            ... '''
            >>> variables = {"id": "gid://shopify/Product/123"}
            >>> data = self._execute_query(query, variables)
            >>> print(data["product"]["title"])
        
        Note:
            - This is an internal method not intended for direct external use
            - Request timeout is set to 30 seconds
            - All requests use POST method as required by GraphQL
            - Response is expected to be valid JSON
        """
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        response = requests.post(
            self.store_url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
            
        return data.get("data", {})
    
    def search_products(
        self,
        req: SearchProductsRequest
    ) -> SearchProductsResponse:
        """Search for products in the Shopify store catalog.
        
        Executes a product search query using Shopify's GraphQL Storefront API,
        retrieving products that match the search criteria with full details
        including variants, images, and pricing information.
        
        The method constructs a GraphQL query, executes it against Shopify,
        and transforms the response into standardized Product objects.
        
        Args:
            req (SearchProductsRequest): Search parameters containing:
                - query (str): Text to search in product titles, descriptions, tags.
                  Empty string returns all products.
                - first (int): Max products to return. Will be capped at 250 (Shopify limit).
                - sort_key (str): Sort field (RELEVANCE, TITLE, PRICE, CREATED_AT, etc.)
                - reverse (bool): Whether to reverse sort order.
        
        Returns:
            SearchProductsResponse: Response containing:
                - products (list[Product]): List of matching products with:
                    - Basic info (id, title, description)
                    - Images (up to 5 per product)
                    - Variants (up to 10 per product) with individual pricing
                    - Price range (min/max) for multi-variant products
                    - Single price for single-variant products
        
        Raises:
            Exception: If the search fails due to:
                - Network/connection errors
                - Invalid authentication
                - GraphQL query errors
                - Response parsing failures
        
        Example:
            >>> client = ShopifyGraphQLClient(store_url="...", access_token="...")
            >>> 
            >>> # Search for shoes, sorted by relevance
            >>> response = client.search_products(
            ...     SearchProductsRequest(
            ...         query="running shoes",
            ...         first=20,
            ...         sort_key="RELEVANCE",
            ...         reverse=False
            ...     )
            ... )
            >>> 
            >>> for product in response.products:
            ...     print(f"{product.title}: ${product.price.amount}")
            ...     if product.variants:
            ...         print(f"  {len(product.variants)} variants available")
        
        Note:
            - Shopify enforces a maximum of 250 products per request
            - Products with single variants have simplified structure (price field)
            - Products with multiple variants include priceRange field
            - Images are limited to 5 per product in the query
            - Variants are limited to 10 per product in the query
            - Empty variant lists are removed from the response
        """

        graphql_query = """
        query searchProducts($query: String!, $first: Int!, $sortKey: ProductSortKeys!, $reverse: Boolean!) {
            products(query: $query, first: $first, sortKey: $sortKey, reverse: $reverse) {
                edges {
                    node {
                        id
                        title
                        description
                        images(first: 5) {
                            edges {
                                node {
                                    url
                                }
                            }
                        }
                        variants(first: 10) {
                            edges {
                                node {
                                    id
                                    title
                                    price {
                                        amount
                                        currencyCode
                                    }
                                }
                            }
                        }
                        priceRange {
                            minVariantPrice {
                                amount
                                currencyCode
                            }
                            maxVariantPrice {
                                amount
                                currencyCode
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {
            "query": req.query,
            "first": min(req.first, 250),  # Shopify limit
            "sortKey": req.sort_key,
            "reverse": req.reverse
        }
        
        try:
            data = self._execute_query(graphql_query, variables)
            products: list[Product] = []

            for edge in data.get("products", {}).get("edges", []):
                product = edge["node"]
                
                # Format images
                images = []
                for img_edge in product.get("images", {}).get("edges", []):
                    images.append(img_edge["node"]["url"])
                product["images"] = images
                
                # Format variants
                variants = []
                for var_edge in product.get("variants", {}).get("edges", []):
                    variants.append(var_edge["node"])
                product["variants"] = variants

                # For single variant products, simplify the structure but keep at least one variant
                if len(product.get("variants", [])) <= 1:
                    price = product.get("priceRange").get("minVariantPrice")
                    product["price"] = price
                    product.pop("priceRange")
                
                products.append(Product(**product))
            
            return SearchProductsResponse(products=products)
            
        except Exception as e:
            raise Exception(f"Failed to search products: {str(e)}")


    def cart_create(self, req: CartCreateRequest) -> CartCreateResponse:
        """Create a new shopping cart in the Shopify store.
        
        Creates a cart using Shopify's cartCreate mutation, optionally including
        initial line items, buyer identification, and delivery address preferences.
        The cart is persisted on Shopify's servers and returns a unique ID and
        checkout URL.
        
        The method handles the complete cart creation flow including:
        - Adding line items with quantities
        - Associating buyer identity (email, phone)
        - Setting delivery addresses
        - Retrieving cost calculations
        - Collecting validation errors and warnings
        
        Args:
            req (CartCreateRequest): Cart creation parameters containing:
                - lines (list[CartLineInput] | None): Items to add. Each specifies
                  a ProductVariant ID (merchandiseId) and quantity. Can be None
                  to create an empty cart.
                - buyer_identity (BuyerIdentity | None): Customer info (email, phone)
                  for order communication and tracking.
                - delivery (CartDeliveryInput | None): Delivery address options with
                  selection status for shipping.
        
        Returns:
            CartCreateResponse: Response containing:
                - cart (Cart): Created cart with:
                    - id (str): Unique cart identifier for future operations
                    - checkout_url (str): Direct URL to proceed to checkout
                    - total_quantity (int): Total items in cart
                    - cost (Cost): Price breakdown (subtotal, tax, total)
                    - Full line items, buyer identity, and delivery info
                - user_errors (list[UserError]): Validation errors if any occurred.
                  Non-empty list indicates cart may not be valid.
                - warnings (list[CartWarning]): Non-fatal warnings (e.g., low stock)
        
        Raises:
            Exception: If cart creation fails due to:
                - Network/connection errors
                - Invalid authentication
                - Invalid product variant IDs
                - GraphQL query errors
                - Response parsing failures
        
        Example:
            >>> # Create cart with items and customer info
            >>> response = client.cart_create(
            ...     CartCreateRequest(
            ...         lines=[
            ...             CartLineInput(
            ...                 merchandiseId="gid://shopify/ProductVariant/123",
            ...                 quantity=2
            ...             )
            ...         ],
            ...         buyerIdentity=BuyerIdentity(
            ...             email="customer@example.com",
            ...             phone="+1234567890"
            ...         ),
            ...         delivery=CartDeliveryInput(
            ...             addresses=[
            ...                 AddressOption(
            ...                     selected=True,
            ...                     address=CartAddressInput(
            ...                         deliveryAddress=Address(
            ...                             address1="123 Main St",
            ...                             city="New York",
            ...                             countryCode="US",
            ...                             zip="10001"
            ...                         )
            ...                     )
            ...                 )
            ...             ]
            ...         )
            ...     )
            ... )
            >>> 
            >>> if response.user_errors:
            ...     print("Errors:", [e.message for e in response.user_errors])
            >>> else:
            ...     print(f"Cart ID: {response.cart.id}")
            ...     print(f"Checkout: {response.cart.checkout_url}")
            ...     print(f"Total: ${response.cart.cost.total_amount.amount}")
        
        Note:
            - Cart IDs are temporary and expire after period of inactivity
            - Line items limited to 250 per cart (Shopify limit)
            - Prices and stock are validated at creation time
            - Checkout URL can be used to redirect customer to complete purchase
            - Delivery groups (first 10) are included in response
        """
        
        graphql_mutation = """
        mutation cartCreate($input: CartInput!) {
            cartCreate(input: $input) {
                cart {
                    id
                    checkoutUrl
                    totalQuantity
                    cost {
                        subtotalAmount {
                            amount
                            currencyCode
                        }
                        totalTaxAmount {
                            amount
                            currencyCode
                        }
                        totalAmount {
                            amount
                            currencyCode
                        }
                    }
                    lines(first: 250) {
                        edges {
                            node {
                                id
                                quantity
                                merchandise {
                                    ... on ProductVariant {
                                        id
                                        title
                                        product {
                                            id
                                            title
                                        }
                                        price {
                                            amount
                                            currencyCode
                                        }
                                    }
                                }
                            }
                        }
                    }
                    buyerIdentity {
                        email
                        phone
                        countryCode
                    }
                    deliveryGroups(first: 10) {
                        edges {
                            node {
                                id
                                selectedDeliveryOption {
                                    handle
                                    title
                                }
                                deliveryAddress {
                                    ... on MailingAddress {
                                        address1
                                        address2
                                        city
                                        countryCode
                                        zip
                                        phone
                                        firstName
                                        lastName
                                    }
                                }
                            }
                        }
                    }
                }
                userErrors {
                    field
                    message
                }
                warnings {
                    message
                }
            }
        }
        """
        
        variables = {
            "input": req.model_dump(exclude_none=True, by_alias=True)
        }
        
        try:
            data = self._execute_query(graphql_mutation, variables)
            cart_create_data = data.get("cartCreate", {})

            cart_data = cart_create_data.get("cart", {})
            user_errors = cart_create_data.get("userErrors", [])
            warnings = cart_create_data.get("warnings", [])
            
            return CartCreateResponse(
                cart=Cart(**cart_data),
                userErrors=user_errors,
                warnings=warnings
            )
            
        except Exception as e:
            raise Exception(f"Failed to create cart: {str(e)}")


    def cart_get(self, req: CartGetRequest) -> CartGetResponse:
        """Retrieve an existing shopping cart by its unique identifier.
        
        Fetches the current state of a previously created cart from Shopify,
        including all items, quantities, pricing, and checkout information.
        Useful for resuming a shopping session or checking cart status.
        
        Args:
            req (CartGetRequest): Request containing:
                - id (str): The cart's unique identifier (e.g., "gid://shopify/Cart/abc123")
                  returned from cart_create operation.
        
        Returns:
            CartGetResponse: Response containing:
                - cart (Cart): Complete cart object with:
                    - id (str): Cart identifier
                    - checkout_url (str): URL to proceed to checkout
                    - total_quantity (int): Total items in cart
                    - cost (Cost): Current price breakdown (subtotal, total)
        
        Raises:
            Exception: If cart retrieval fails due to:
                - Cart not found (invalid or expired ID)
                - Network/connection errors
                - Invalid authentication
                - GraphQL query errors
                - Response parsing failures
        
        Example:
            >>> # Create a cart first
            >>> create_response = client.cart_create(CartCreateRequest(...))
            >>> cart_id = create_response.cart.id
            >>> 
            >>> # Later, retrieve the cart
            >>> response = client.cart_get(CartGetRequest(id=cart_id))
            >>> print(f"Cart has {response.cart.total_quantity} items")
            >>> print(f"Total: ${response.cart.cost.total_amount.amount}")
            >>> print(f"Checkout: {response.cart.checkout_url}")
        
        Note:
            - Carts expire after period of inactivity (typically 10 days in Shopify)
            - Prices may change between creation and retrieval
            - Out-of-stock items may be removed automatically
            - Tax amounts may not be included (totalTaxAmount omitted in this query)
        """

        graphql_query = """
        query cart($id: ID!) {
            cart(id: $id) {
                id
                checkoutUrl
                totalQuantity
                cost {
                    subtotalAmount {
                        amount
                        currencyCode
                    }
                    totalAmount {
                        amount
                        currencyCode
                    }
                }
            }
        }
        """

        variables = {
            "id": req.id
        }

        try:
            data = self._execute_query(graphql_query, variables)
            cart_data = data.get("cart")
            
            if cart_data is None:
                raise Exception(f"Cart with id {id} not found")
            
            return CartGetResponse(cart=Cart(**cart_data))
            
        except Exception as e:
            raise Exception(f"Failed to get cart: {str(e)}")


if __name__ == "__main__":
    """
    Quick integration test demonstrating client usage.
    
    Tests product search, cart creation, and cart retrieval in sequence.
    Uses the default store configuration for testing purposes.
    """
    client = ShopifyGraphQLClient(store_url="https://huescorner.myshopify.com/api/2025-10/graphql.json")
    
    # Test 1: Search for products
    print("=== Product Search Test ===")
    search_resp = client.search_products(SearchProductsRequest(query="bag", first=10))
    print(f"Found {len(search_resp.products)} products")
    for prod in search_resp.products:
        print(f"{prod.model_dump_json()}")
    print()
    
    # Test 2: Create cart with first available variant
    print("=== Cart Creation Test ===")
    lines = []
    for product in search_resp.products:
        lines.append(CartLineInput(merchandiseId=product.variants[0].id, quantity=1))
    
    if lines:
        cart_req = CartCreateRequest(
            lines=lines,
            buyerIdentity=BuyerIdentity(email="test@example.com"),
            delivery=CartDeliveryInput(
                addresses=[
                    AddressOption(
                        selected=True,
                        address=CartAddressInput(
                            deliveryAddress=Address(
                                address1="123 Main St",
                                address2="Apt 4B",
                                city="New York",
                                countryCode="US",
                                zip="10001",
                                firstName="John",
                                lastName="Doe",
                                phone="+1234567890",
                            )
                        )
                    )
                ]
            ),
        )
        cart_resp = client.cart_create(cart_req)
        
        if cart_resp.user_errors or cart_resp.warnings:
            print(f"Errors: {[e.message for e in cart_resp.user_errors]}")
            print(f"Warnings: {[w.message for w in cart_resp.warnings]}")
        else:
            print(f"Cart created: {cart_resp.cart.id}")
            print(f"Total: ${cart_resp.cart.cost.total_amount.amount}")
            print("Cart:")
            print(cart_resp.cart.model_dump_json())
            print()
            
            # Test 3: Retrieve cart
            print("=== Cart Retrieval Test ===")
            get_resp = client.cart_get(CartGetRequest(id=cart_resp.cart.id))
            print(f"Retrieved cart with {get_resp.cart.total_quantity} items")
            print("Cart:")
            print(get_resp.cart.model_dump_json())
    else:
        print("No products with variants found for testing")
    
    print("\n=== Tests Complete ===")

