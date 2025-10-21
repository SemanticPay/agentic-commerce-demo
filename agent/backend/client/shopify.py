import requests
import logging
import sys
from typing import Dict, Any, Optional

from agent.backend.client.base_types import Address, AddressOption, BuyerIdentity, Cart, CartAddressInput, CartCreateRequest, CartCreateResponse, CartDeliveryInput, CartGetRequest, CartGetResponse, CartLineInput, Product, SearchProductsRequest, SearchProductsResponse
from agent.backend.client.interface import StoreFrontClient

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)



class ShopifyGraphQLClient(StoreFrontClient):
    def __init__(self, store_url: str, access_token: Optional[str] = None):
        logger.info("Initializing ShopifyGraphQLClient")
        logger.info(f"Store URL: {store_url}")
        logger.info(f"Access token provided: {bool(access_token)}")
        
        self.store_url = store_url
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
        }
        
        if access_token:
            self.headers["X-Shopify-Storefront-Access-Token"] = access_token
            logger.info("Access token added to headers")
        
        logger.info("ShopifyGraphQLClient initialized successfully")
    
    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.debug("Executing GraphQL query")
        logger.debug(f"Variables: {variables}")
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            logger.info(f"Sending POST request to {self.store_url}")
            response = requests.post(
                self.store_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            logger.info(f"Received response with status code: {response.status_code}")
            
            response.raise_for_status()
            logger.debug("HTTP request successful")
            
            data = response.json()
            logger.debug("Response parsed as JSON")
            
            if "errors" in data:
                logger.error(f"GraphQL errors in response: {data['errors']}")
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            logger.debug("GraphQL query executed successfully")
            return data.get("data", {})
            
        except requests.Timeout as e:
            logger.error("Request timed out after 30 seconds", exc_info=True)
            raise
        except requests.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error executing GraphQL query: {str(e)}", exc_info=True)
            raise
    
    def search_products(
        self,
        req: SearchProductsRequest
    ) -> SearchProductsResponse:
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
        
        logger.info(f"Capped 'first' to {variables['first']} (Shopify max: 250)")
        
        try:
            logger.info("Executing product search GraphQL query")
            data = self._execute_query(graphql_query, variables)
            logger.info("Product search query executed successfully")
            
            products: list[Product] = []
            edges = data.get("products", {}).get("edges", [])
            logger.info(f"Processing {len(edges)} product(s) from response")

            for idx, edge in enumerate(edges):
                product = edge["node"]
                logger.debug(f"Processing product {idx + 1}/{len(edges)}: {product.get('title')}")
                
                # Format images
                images = []
                for img_edge in product.get("images", {}).get("edges", []):
                    images.append(img_edge["node"]["url"])
                product["images"] = images
                logger.debug(f"Formatted {len(images)} image(s)")
                
                # Format variants
                variants = []
                for var_edge in product.get("variants", {}).get("edges", []):
                    variants.append(var_edge["node"])
                product["variants"] = variants
                logger.debug(f"Formatted {len(variants)} variant(s)")

                # For single variant products, simplify the structure but keep at least one variant
                if len(product.get("variants", [])) <= 1:
                    price = product.get("priceRange").get("minVariantPrice")
                    product["price"] = price
                    product.pop("priceRange")
                    logger.debug("Simplified price structure for single-variant product")
                
                products.append(Product(**product))
                logger.debug(f"Product {idx + 1} processed and added to list")
            
            logger.info(f"Successfully processed {len(products)} product(s)")
            logger.info("="*60)
            return SearchProductsResponse(products=products)
            
        except Exception as e:
            logger.error(f"Failed to search products: {str(e)}", exc_info=True)
            raise Exception(f"Failed to search products: {str(e)}")


    def cart_create(self, req: CartCreateRequest) -> CartCreateResponse:
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
        
        logger.info("Prepared cart creation variables")
        logger.debug(f"Variables: {variables}")
        
        try:
            logger.info("Executing cart creation GraphQL mutation")
            data = self._execute_query(graphql_mutation, variables)
            logger.info("Cart creation mutation executed successfully")
            
            cart_create_data = data.get("cartCreate", {})

            cart_data = cart_create_data.get("cart", {})
            user_errors = cart_create_data.get("userErrors", [])
            warnings = cart_create_data.get("warnings", [])
            
            if user_errors:
                logger.warning(f"Cart creation returned {len(user_errors)} user error(s)")
                for error in user_errors:
                    logger.warning(f"User error: {error.get('message')} (field: {error.get('field')})")
            
            if warnings:
                logger.info(f"Cart creation returned {len(warnings)} warning(s)")
                for warning in warnings:
                    logger.info(f"Warning: {warning.get('message')}")
            
            if cart_data:
                logger.info(f"Cart created with ID: {cart_data.get('id')}")
                logger.info(f"Cart total quantity: {cart_data.get('totalQuantity')}")
                logger.info(f"Checkout URL: {cart_data.get('checkoutUrl')}")
                cost = cart_data.get('cost', {})
                if cost:
                    subtotal = cost.get('subtotalAmount', {})
                    total = cost.get('totalAmount', {})
                    logger.info(f"Subtotal: {subtotal.get('amount')} {subtotal.get('currencyCode')}")
                    logger.info(f"Total: {total.get('amount')} {total.get('currencyCode')}")
            else:
                logger.info("No cart data returned")
                cart_data = {}
            
            logger.info("="*60)

            cart = None
            if cart_data:
                cart = Cart(**cart_data)

            return CartCreateResponse(
                cart=cart,
                userErrors=user_errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Failed to create cart: {str(e)}", exc_info=True)
            raise Exception(f"Failed to create cart: {str(e)}")


    def cart_get(self, req: CartGetRequest) -> CartGetResponse:
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
            logger.info("Executing cart retrieval GraphQL query")
            data = self._execute_query(graphql_query, variables)
            logger.info("Cart retrieval query executed successfully")
            
            cart_data = data.get("cart")
            
            if cart_data is None:
                logger.error(f"Cart with id {req.id} not found")
                raise Exception(f"Cart with id {req.id} not found")
            
            logger.info(f"Cart retrieved with ID: {cart_data.get('id')}")
            logger.info(f"Cart total quantity: {cart_data.get('totalQuantity')}")
            logger.info(f"Checkout URL: {cart_data.get('checkoutUrl')}")
            cost = cart_data.get('cost', {})
            if cost:
                subtotal = cost.get('subtotalAmount', {})
                total = cost.get('totalAmount', {})
                logger.info(f"Subtotal: {subtotal.get('amount')} {subtotal.get('currencyCode')}")
                logger.info(f"Total: {total.get('amount')} {total.get('currencyCode')}")
            
            logger.info("="*60)
            return CartGetResponse(cart=Cart(**cart_data))
            
        except Exception as e:
            logger.error(f"Failed to get cart: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get cart: {str(e)}")


if __name__ == "__main__":
    """
    Quick integration test demonstrating client usage.
    
    Tests product search, cart creation, and cart retrieval in sequence.
    Uses the default store configuration for testing purposes.
    """
    logger.info("="*60)
    logger.info("Starting Shopify client integration tests")
    logger.info("="*60)
    
    client = ShopifyGraphQLClient(store_url="https://huescorner.myshopify.com/api/2025-10/graphql.json")
    
    # Test 1: Search for products
    logger.info("TEST 1: Product Search")
    print("=== Product Search Test ===")
    search_resp = client.search_products(SearchProductsRequest(query="bag", first=10))
    print(f"Found {len(search_resp.products)} products")
    logger.info(f"Product search test completed: {len(search_resp.products)} products found")
    for prod in search_resp.products:
        print(f"{prod.model_dump_json()}")
    print()
    
    # Test 2: Create cart with first available variant
    logger.info("TEST 2: Cart Creation")
    print("=== Cart Creation Test ===")
    lines = []
    for product in search_resp.products:
        lines.append(CartLineInput(merchandiseId=product.variants[0].id, quantity=1))
    
    logger.info(f"Prepared {len(lines)} line items for cart")
    
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
            logger.warning("Cart creation completed with errors or warnings")
        else:
            print(f"Cart created: {cart_resp.cart.id}") # type: ignore
            print(f"Total: ${cart_resp.cart.cost.total_amount.amount}") # type: ignore
            print("Cart:")
            print(cart_resp.cart.model_dump_json()) # type: ignore
            print()
            logger.info("Cart creation test completed successfully")
            
            # Test 3: Retrieve cart
            logger.info("TEST 3: Cart Retrieval")
            print("=== Cart Retrieval Test ===")
            get_resp = client.cart_get(CartGetRequest(id=cart_resp.cart.id)) # type: ignore
            print(f"Retrieved cart with {get_resp.cart.total_quantity} items")
            print("Cart:")
            print(get_resp.cart.model_dump_json())
            logger.info("Cart retrieval test completed successfully")
    else:
        print("No products with variants found for testing")
        logger.warning("No products with variants available for cart creation test")
    
    print("\n=== Tests Complete ===")
    logger.info("="*60)
    logger.info("All integration tests completed")
    logger.info("="*60)

