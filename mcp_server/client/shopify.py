import requests
from typing import List, Dict, Any, Optional
import json
from client.base_types import Product, SearchProductsResponse, CartInput, CartCreateResponse
from client.interface import StoreFrontClient


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
        query: str = "",
        first: int = 10,
        sort_key: str = "RELEVANCE",
        reverse: bool = False
    ) -> SearchProductsResponse:
        """
        Search for products using the Shopify Storefront API.
        
        Args:
            query: Search query string (e.g., "shoes", "red", "nike")
            first: Number of products to return (max 250)
            sort_key: Sort key (RELEVANCE, TITLE, PRICE, CREATED_AT, etc.)
            reverse: Whether to reverse the sort order
            
        Returns:
            List of product dictionaries containing id, title, description, etc.
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
            "query": query,
            "first": min(first, 250),  # Shopify limit
            "sortKey": sort_key,
            "reverse": reverse
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

                # For single vaiant products
                if len(product.get("variants", [])) <= 1:
                    product.pop("variants")
                    price = product.get("priceRange").get("minVariantPrice")
                    product["price"] = price
                    product.pop("priceRange")
                
                products.append(Product(**product))
            
            return SearchProductsResponse(products=products)
            
        except Exception as e:
            raise Exception(f"Failed to search products: {str(e)}")


    def create_cart(self, cart_input: CartInput) -> CartCreateResponse:
        """
        Create a new cart using the Shopify Storefront API.
        
        Args:
            cart_input: CartInput object containing cart data (lines, attributes, etc.)
            
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
                    buyerIdentity {
                        email
                        phone
                        companyLocationId
                        countryCode
                        customerAccessToken
                        preferences
                        purchasingCompany
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
                    createdAt
                    updatedAt
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
            "input": cart_input.model_dump(exclude_none=True, by_alias=True)
        }
        
        try:
            data = self._execute_query(graphql_mutation, variables)
            cart_create_data = data.get("cartCreate", {})
            
            cart_data = cart_create_data.get("cart")
            user_errors = cart_create_data.get("userErrors", [])
            warnings = cart_create_data.get("warnings", [])
            
            return CartCreateResponse(
                cart=cart_data,
                user_errors=user_errors,
                warnings=warnings
            )
            
        except Exception as e:
            raise Exception(f"Failed to create cart: {str(e)}")
            

    def get_cart(self):
        raise NotImplementedError("Cart functionality is not implemented yet.")  

    def add_to_cart(self, product_id: str, quantity: int = 1):
        raise NotImplementedError("Add to cart functionality is not implemented yet.")

    def remove_from_cart(self, product_id: str):
        raise NotImplementedError("Remove from cart functionality is not implemented yet.")

    def get_payment_url(self, cart_id: str) -> str:
        raise NotImplementedError("Payment URL functionality is not implemented yet.")

    def get_payment_status(self, order_id: str) -> str:
        raise NotImplementedError("Payment status functionality is not implemented yet.")

if __name__ == "__main__":
    client = ShopifyGraphQLClient()
    resp = client.search_products(query="bag", first=5)
    print(resp.model_dump_json(exclude_none=True))
