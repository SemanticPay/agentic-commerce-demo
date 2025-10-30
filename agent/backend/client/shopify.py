import json
import os
from dotenv import load_dotenv
import requests
import logging
import sys
from typing import Dict, Any, Optional

from agent.backend.client.base_types import Address, AddressOption, Cart, CartAddressInput, CartCreateRequest, CartCreateResponse, CartGetRequest, CartGetResponse, CartLineInput, GetProductRequest, GetProductResponse, GetProductsRequest, GetProductsResponse, Product, SearchProductsRequest, SearchProductsResponse
from agent.backend.client.interface import ProductsClient, StoreFrontClient
from google.adk.agents import Agent
import asyncio

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

import asyncio
from google.adk.agents import Agent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import re

def expand_query_for_shopify(raw_query: str) -> str:
    if not raw_query:
        return raw_query
    tokens = re.findall(r"\w+", raw_query.lower())
    expanded = []
    for t in tokens:
        if t.endswith("s"):
            singular = t[:-1]
            expanded.append(f"{t} OR {singular}")
        else:
            plural = f"{t}s"
            expanded.append(f"{t} OR {plural}")
    inclusive_query = " OR ".join(expanded)
    return inclusive_query

class ShopifyGraphQLClient(StoreFrontClient):
    def __init__(self, store_url: str, access_token: Optional[str] = None):
        logger.info("Initializing ShopifyGraphQLClient")
        logger.info(f"Store URL: {store_url}")
        logger.info(f"Access token provided: {bool(access_token)}")
        
        self.store_url = "https://huescorner.myshopify.com/api/2025-10/graphql.json"
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

    def fetch_all_products(self) -> GetProductsResponse:
        """
        Retrieve all published products from Shopify Storefront API with images and detailed logging.
        """
        logger.info("=" * 60)
        logger.info("Starting full product catalog fetch from Shopify Storefront API")
        logger.info("=" * 60)

        products = []
        cursor = None
        page = 1

        query = """
        query($cursor:String){
        products(first:250, after:$cursor){
            edges{
            cursor
            node{
                id
                handle
                title
                description
                vendor
                productType
                tags
                onlineStoreUrl
                images(first:5){
                edges{
                    node{ url }
                }
                }
                variants(first:20){
                edges{
                    node{
                    id
                    title
                    price{amount currencyCode}
                    }
                }
                }
            }
            }
            pageInfo{hasNextPage endCursor}
        }
        }
        """

        try:
            while True:
                logger.info(f"Fetching page {page} (cursor: {cursor})")
                resp = self._execute_query(query, {"cursor": cursor})

                if "errors" in resp:
                    logger.error(f"GraphQL error(s): {resp['errors']}")
                    raise RuntimeError(f"GraphQL errors: {resp['errors']}")

                if "products" not in resp:
                    logger.error(f"Missing 'products' key in response: {json.dumps(resp)[:500]}")
                    raise RuntimeError("Invalid Shopify response: no products key")

                products_data = resp["products"]
                edges = products_data.get("edges", [])
                logger.info(f"Page {page}: {len(edges)} product(s) retrieved")

                for i, edge in enumerate(edges):
                    node = edge.get("node")
                    if not node:
                        logger.warning(f"Edge {i} missing node")
                        continue

                    # Images
                    image_edges = node.get("images", {}).get("edges", [])
                    images = [img["node"]["url"] for img in image_edges if "node" in img and "url" in img["node"]]
                    node["images"] = images or ["https://via.placeholder.com/300"]

                    # Variants
                    variant_edges = node.get("variants", {}).get("edges", [])
                    variants = []
                    for idx, v in enumerate(variant_edges):
                        vn = v.get("node", {})
                        vn.setdefault("id", f"{node['id']}_variant_{idx}")
                        vn.setdefault("title", "Default Variant")
                        vn.setdefault("price", {"amount": "0", "currencyCode": "USD"})
                        variants.append(vn)
                    node["variants"] = variants
                    node["price"] = variants[0]["price"] if variants else {"amount": "0", "currencyCode": "USD"}

                    # Fill defaults
                    node.setdefault("vendor", "Unknown")
                    node.setdefault("productType", "")
                    node.setdefault("tags", [])
                    node.setdefault("description", "")
                    node.setdefault("onlineStoreUrl", "")

                    try:
                        product = Product(**node)
                        products.append(product)
                        logger.debug(f"Processed product {i + 1}: {product.title}")
                    except Exception as ex:
                        logger.error(f"Validation error building Product: {ex}", exc_info=True)

                page_info = products_data.get("pageInfo", {})
                has_next = page_info.get("hasNextPage")
                cursor = page_info.get("endCursor")

                logger.info(f"Page {page} processed. hasNextPage={has_next}, endCursor={cursor}")
                if not has_next:
                    break

                page += 1

            logger.info(f"Fetch complete. Total products: {len(products)}")
            logger.info("=" * 60)
            return GetProductsResponse(products=products)

        except Exception as e:
            logger.error(f"Failed to fetch all products: {e}", exc_info=True)
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
                        onlineStoreUrl
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
        req.query = expand_query_for_shopify(req.query)
  
        variables = {
            "query": req.query,
            "first": min(req.first, 250),
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


                print("===================")
                print("product", product)
                print("===================")

                
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
        
        # Only pass lines to the mutation
        variables = {
            "input": {
                "lines": [line.model_dump(by_alias=True) for line in (req.lines or [])]
            }
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

    def get_product(self, req: GetProductRequest) -> GetProductResponse:
        """
        Retrieve a specific product by its handle or ID from Shopify Storefront API.
        
        Args:
            req (GetProductRequest): Request containing either handle or id
            
        Returns:
            GetProductResponse: Response containing the product or None if not found
        """
        
        # Build the query based on what's provided (id takes precedence)
        graphql_query = """
        query getProduct($id: ID!) {
            product(id: $id) {
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
        """
        variables = {"id": req.id}
        logger.info(f"Fetching product by ID: {req.id}")
        
        try:
            logger.info("Executing product retrieval GraphQL query")
            data = self._execute_query(graphql_query, variables)
            logger.info("Product retrieval query executed successfully")
            
            product_data = data.get("product")
            
            if product_data is None:
                logger.info(f"Product not found: {req.id}")
                return GetProductResponse(product=None)
            
            logger.info(f"Product found: {product_data.get('title')}")
            
            # Format images
            images = []
            for img_edge in product_data.get("images", {}).get("edges", []):
                images.append(img_edge["node"]["url"])
            product_data["images"] = images
            logger.debug(f"Formatted {len(images)} image(s)")
            
            # Format variants
            variants = []
            for var_edge in product_data.get("variants", {}).get("edges", []):
                variants.append(var_edge["node"])
            product_data["variants"] = variants
            logger.debug(f"Formatted {len(variants)} variant(s)")
            
            # For single variant products, simplify the structure
            if len(product_data.get("variants", [])) <= 1:
                price = product_data.get("priceRange", {}).get("minVariantPrice")
                if price:
                    product_data["price"] = price
                    product_data.pop("priceRange", None)
                    logger.debug("Simplified price structure for single-variant product")
            
            product = Product(**product_data)
            logger.info(f"Successfully retrieved product: {product.title}")
            logger.info("="*60)
            return GetProductResponse(product=product)
            
        except Exception as e:
            logger.error(f"Failed to get product: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get product: {str(e)}")


def test_storefront_client():
    """
    Quick integration test demonstrating client usage.
    
    Tests product search, cart creation, and cart retrieval in sequence.
    Uses the default store configuration for testing purposes.
    """
    logger.info("="*60)
    logger.info("Starting Shopify client integration tests")
    logger.info("="*60)
    
    load_dotenv()
    client = ShopifyGraphQLClient(store_url=os.getenv("SHOPIFY_STOREFRONT_STORE_URL", ""),)
    
    # Test 1: Search for products
    logger.info("TEST 1: Product Search")
    print("=== Product Search Test ===")
    search_resp = client.search_products(SearchProductsRequest(query="bag", first=10))
    print(f"Found {len(search_resp.products)} products")
    logger.info(f"Product search test completed: {len(search_resp.products)} products found")
    for prod in search_resp.products:
        print(f"{prod.model_dump_json()}")
    print()


    logger.info("TEST 1.5: Product Get")
    print("=== Product Get Test ===")
    get_resp = client.get_product(GetProductRequest(id=search_resp.products[0].id))
    print("PRODUCT ===> ", get_resp.product.model_dump_json())
    print()
    
    # Test 2: Create cart with first available variant
    logger.info("TEST 2: Cart Creation")
    print("=== Cart Creation Test ===")
    lines = []
    for product in search_resp.products:
        lines.append(CartLineInput(merchandiseId=product.variants[0].id, quantity=1))
    
    logger.info(f"Prepared {len(lines)} line items for cart")
    
    if lines:
        cart_req = CartCreateRequest(lines=lines)
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


class ShopifyAdminClient(ProductsClient):
    def __init__(self, store_url: str, access_token: str):
        self.store_url = "https://huescorner.myshopify.com/api/2025-10/graphql.json"
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token,
        }

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

    def get_products(self, req: GetProductsRequest) -> GetProductsResponse:
        """
        Fetch products from Shopify Admin API with automatic pagination support.
        
        Args:
            req (GetProductsRequest): Request object containing number of products to fetch. 
        
        Returns:
            GetProductsResponse containing all requested products
        """
        graphql_query = """
        query getProducts($first: Int!, $after: String) {
            products(first: $first, after: $after) {
                edges {
                    cursor
                    node {
                        id
                        title
                        description
                        onlineStoreUrl
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
                                    price
                                }
                            }
                        }
                        priceRangeV2 {
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
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """
        
        all_products: list[Product] = []
        remaining = req.num_results
        after_cursor = None
        
        logger.info(f"Starting to fetch {req.num_results} product(s) from Shopify Admin API")
        
        try:
            while remaining > 0:
                # Fetch up to 250 products per page (Shopify's limit)
                page_size = min(remaining, 250)
                
                variables = {
                    "first": page_size,
                    "after": after_cursor
                }
                
                logger.info(f"Fetching page with {page_size} products (cursor: {after_cursor})")
                data = self._execute_query(graphql_query, variables)
                logger.info("Product query executed successfully")
                
                products_data = data.get("products", {})
                edges = products_data.get("edges", [])
                page_info = products_data.get("pageInfo", {})
                
                logger.info(f"Retrieved {len(edges)} product(s) in this page")
                
                # Process products from this page
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
                        variant_node = var_edge["node"]
                        # Admin API returns price as string, need to format it
                        variant_node["price"] = {
                            "amount": variant_node["price"],
                            "currencyCode": "USD"  # Default, will be overridden by priceRange if available
                        }
                        variants.append(variant_node)
                    product["variants"] = variants
                    logger.debug(f"Formatted {len(variants)} variant(s)")
                    
                    # Rename priceRangeV2 to priceRange for consistency
                    if "priceRangeV2" in product:
                        product["priceRange"] = product.pop("priceRangeV2")
                    
                    # For single variant products, simplify the structure
                    if len(product.get("variants", [])) <= 1:
                        price = product.get("priceRange", {}).get("minVariantPrice")
                        if price:
                            product["price"] = price
                            product.pop("priceRange", None)
                        logger.debug("Simplified price structure for single-variant product")
                    
                    all_products.append(Product(**product))
                    logger.debug(f"Product {idx + 1} processed and added to list")
                
                remaining -= len(edges)
                logger.info(f"Processed {len(all_products)} total products so far, {remaining} remaining")
                
                # Check if we need to fetch more pages
                has_next_page = page_info.get("hasNextPage", False)
                after_cursor = page_info.get("endCursor")
                
                if not has_next_page or remaining <= 0:
                    logger.info("No more pages to fetch or target count reached")
                    break
                
                if not after_cursor:
                    logger.warning("hasNextPage is true but no endCursor provided")
                    break
            
            logger.info(f"Successfully fetched {len(all_products)} product(s)")
            logger.info("="*60)
            return GetProductsResponse(products=all_products)
            
        except Exception as e:
            logger.error(f"Failed to get products: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get products: {str(e)}")
        
    
def test_admin_client():
    load_dotenv()
    admin_client = ShopifyAdminClient(
        store_url=os.getenv("SHOPIFY_ADMIN_API_STORE_URL", ""),
        access_token=os.getenv("SHOPIFY_ADMIN_API_ACCESS_TOKEN", "")
    )

    products = admin_client.get_products(GetProductsRequest(num_results=100))
    print(products.model_dump_json(indent=2))

if __name__ == "__main__":
    test_storefront_client()
    # test_admin_client()
