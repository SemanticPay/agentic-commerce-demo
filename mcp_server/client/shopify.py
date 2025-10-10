import requests
from typing import List, Dict, Any, Optional
import json
from base_types import Address, AddressOption, BuyerIdentity, CartAddressInput, CartDeliveryInput, Product, SearchProductsRequest, SearchProductsResponse, CartCreateRequest, CartCreateResponse, Cart, CartLineInput
from interface import StoreFrontClient


class ShopifyGraphQLClient(StoreFrontClient):
    """
    Shopify Storefront GraphQL API client for searching products.
    """
    
    def __init__(self, store_url: str = "https://huescorner.myshopify.com/api/2025-10/graphql.json", access_token: Optional[str] = None):
        """
        Initialize the Shopify GraphQL client.
        
        Args:
            store_url: The Shopify Storefront API GraphQL endpoint
            access_token: Optional storefront access token for enhanced features
        """
        self.store_url = store_url
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
        }
        
        if access_token:
            self.headers["X-Shopify-Storefront-Access-Token"] = access_token
    
    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query against the Shopify Storefront API.
        
        Args:
            query: The GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            The response data from the API
            
        Raises:
            Exception: If the request fails or returns errors
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
        """
        Search for products using the Shopify Storefront API.
        
        Args:
            req: SearchProductsRequest object containing search parameters 
            
        Returns:
            SearchProductsResponse containing the list of found products
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
                if len(product.get("variants", [])) == 0:
                    # No variants at all, remove the field
                    product.pop("variants", None)
                
                products.append(Product(**product))
            
            return SearchProductsResponse(products=products)
            
        except Exception as e:
            raise Exception(f"Failed to search products: {str(e)}")


    def cart_create(self, req: CartCreateRequest) -> CartCreateResponse:
        """
        Create a new cart using the Shopify Storefront API.
        
        Args:
            req: CartCreateRequest object containing cart data (lines, buyer identity, etc.)
            
        Returns:
            CartCreateResponse containing the created cart, user errors, and warnings
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


    def get_cart(self, id: str):
        """
        Get a cart by id using the Shopify Storefront API.
        
        Args:
            id: The id of the cart
            
        Returns:
            Cart containing the cart data
        """

        graphql_query = """
        query cart($id: ID!) {
            cart(id: $id) {
                id
                checkoutUrl
                totalQuantity
                createdAt
                updatedAt
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
                                    country
                                    countryCodeV2
                                    zip
                                    phone
                                    firstName
                                    lastName
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
                attributes {
                    key
                    value
                }
                discountCodes {
                    code
                    applicable
                }
                note
            }
        }
        """

        variables = {
            "id": id
        }

        try:
            data = self._execute_query(graphql_query, variables)
            cart_data = data.get("cart")
            
            if cart_data is None:
                raise Exception(f"Cart with id {id} not found")
            
            return Cart(**cart_data)
            
        except Exception as e:
            raise Exception(f"Failed to get cart: {str(e)}")

    def add_to_cart(self, cart_id: str, product_id: str, quantity: int = 1):
        pass

    def remove_from_cart(self, cart_id: str, product_id: str):
        pass

    def get_payment_url(self, cart_id: str) -> str:
        return ""

    def get_payment_status(self, order_id: str) -> str:
        return ""

    # def add_to_cart(self, product_id: str, quantity: int = 1):
    #     raise NotImplementedError("Add to cart functionality is not implemented yet.")

    # def remove_from_cart(self, product_id: str):
    #     raise NotImplementedError("Remove from cart functionality is not implemented yet.")

    # def get_payment_url(self, cart_id: str) -> str:
    #     raise NotImplementedError("Payment URL functionality is not implemented yet.")

    # def get_payment_status(self, order_id: str) -> str:
    #     raise NotImplementedError("Payment status functionality is not implemented yet.")

if __name__ == "__main__":
    client = ShopifyGraphQLClient()
    
    # Test 1: Search for products
    print("=== Testing Product Search ===")
    resp = client.search_products(req=SearchProductsRequest(query="bag"))
    print(f"Found {len(resp.products)} products")
    
    if resp.products:
        print(f"\nFirst product: {resp.products[0].title}")
        print(f"Price: {resp.products[0].price.amount} {resp.products[0].price.currency_code}")
    
    # Test 2: Create a cart
    print("\n=== Testing Cart Creation ===")
    if resp.products:
        first_product = resp.products[0]
        
        # Try to get a variant ID from any product
        variant_id = None
        
        # First, try products with explicit variants
        for product in resp.products:
            if hasattr(product, 'variants') and product.variants:
                variant_id = product.variants[0].id
                first_product = product
                print(f"Using product with variants: {product.title}")
                break
        
        # If no variants found, we need to fetch product details to get the default variant
        if not variant_id:
            # For single-variant products in Shopify, we need the variant ID
            # Let's search for products with "first: 10" and hopefully get some with variants
            print("No variants in initial search, trying broader search...")
            resp2 = client.search_products(SearchProductsRequest(query="", first=10))
            for product in resp2.products:
                if hasattr(product, 'variants') and product.variants:
                    variant_id = product.variants[0].id
                    first_product = product
                    print(f"Using product: {product.title}")
                    break
        
        if variant_id:
            cart_input = CartCreateRequest(
                lines=[
                    CartLineInput(
                        merchandiseId=variant_id,
                        quantity=1
                    )
                ],
                buyerIdentity=BuyerIdentity(
                    email="customer@example.com",
                    phone="+12125551234",
                    countryCode="US"
                ),
                delivery=CartDeliveryInput(addresses=[
                    AddressOption(
                        selected=True,
                        address=CartAddressInput(
                            deliveryAddress=Address(
                                address1="123 Main Street",
                                address2="Apt 4B",
                                city="New York",
                                countryCode="US",
                                zip="10001",
                                firstName="John",
                                lastName="Doe",
                                phone="+12125551234"
                            )
                        ),
                    ),
                ])
            )
            
            try:
                cart_response = client.cart_create(cart_input)
                
                print(cart_response.model_dump_json())
                # if cart_response.cart:
                #     print(f"✓ Cart created successfully!")
                #     print(f"  Cart ID: {cart_response.cart.id}")
                #     print(f"  Checkout URL: {cart_response.cart.checkout_url}")
                #     print(f"  Total Quantity: {cart_response.cart.total_quantity}")
                    
                #     # Test 3: Get the cart we just created
                #     print("\n=== Testing Get Cart ===")
                #     try:
                #         retrieved_cart = client.get_cart(cart_response.cart.id)
                #         print(f"✓ Retrieved cart successfully!")
                #         print(f"  Cart ID: {retrieved_cart.id}")
                #         print(f"  Total Quantity: {retrieved_cart.total_quantity}")
                #         print(f"  Checkout URL: {retrieved_cart.checkout_url}")
                #     except Exception as e:
                #         print(f"✗ Failed to retrieve cart: {str(e)}")
                        
                # elif cart_response.user_errors:
                #     print(f"✗ Cart creation failed with errors:")
                #     for error in cart_response.user_errors:
                #         print(f"  - {error.message}")
                # else:
                #     print("✗ Cart creation failed: No cart returned and no errors")
                    
            except Exception as e:
                print(f"✗ Exception during cart creation: {str(e)}")
        else:
            print("✗ No products with variants found to create a cart")
    else:
        print("✗ No products found to create a cart")
    
    print("\n=== Tests Complete ===")
