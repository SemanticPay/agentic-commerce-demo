import logging
import os
import sys
from typing import Optional

from google.adk.tools import ToolContext

from agent.backend.client.base_types import GetProductRequest, SearchProductsRequest, StoreProvider
from agent.backend.client.factory import get_storefront_client
from agent.backend.client.interface import StoreFrontClient
from agent.backend.state import keys
from agent.backend.tools.context.tools import get_search_categories
from agent.backend.types.types import Price, Product, ProductList, ProductSection

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# Initialize storefront client with Shopify
# To use a different store, modify the provider and kwargs here
logger.info("Initializing Shopify storefront client")
storefront_client: StoreFrontClient = get_storefront_client(
    provider=StoreProvider.SHOPIFY,
    store_url=os.getenv("SHOPIFY_STOREFRONT_STORE_URL", "")
)
logger.info("Storefront client initialized successfully")


def search_product_categories(tool_context: ToolContext) -> None:
    categories = get_search_categories(tool_context)

    sections: list[ProductSection] = []
    for cat in categories:
        query = cat.query
        prod_list = search_products(query)
        sections.append(ProductSection(
            title=cat.title,
            description=cat.description,
            subtitle=cat.subtitle,
            products=prod_list.products,
        ))

    logger.info(f"Setting product categories sections in state: {sections}")
    tool_context.state[keys.PRODUCT_SECTIONS_STATE_KEY] = sections


def search_products(query: str) -> ProductList:
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
                - image (str): URL to product image for display
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
                    image=prod.images[0],
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
        return ProductList()


def get_product_details(product_id: str, tool_context: Optional[ToolContext] = None) -> Optional[Product]:
    """Get detailed information for a specific product by ID or handle.
    
    This MCP tool allows AI agents to retrieve complete details about a single
    product from the e-commerce store using either its unique ID or URL handle.
    Use this when the user wants detailed information about a specific product.
    
    **AI Agent Instructions:**
    - Use this tool when the user asks about a specific product by name or after
      they've selected a product from search results
    - Provide either product_id (from search results) or handle (URL-friendly name)
    - Returns full product details including all variants, pricing, and images
    - If product is not found, returns None
    - Present the full product information to the user including available variants
    
    Args:
        product_id (str): Unique product variant ID from search results 
            (e.g., "gid://shopify/ProductVariant/123"). 
            Note: This is a variant ID from search results. If you have a 
            product handle instead, use the handle parameter.
            Default: "" (will use handle instead)
        handle (str): URL-friendly product handle/slug (e.g., "wool-sweater").
            Use this when you know the product name but not the ID.
            Default: "" (will use product_id instead)
        tool_context (ToolContext): Context object provided by the framework.
            Default: None
    
    Returns:
        Product | None: Product object containing:
            - id (str): Unique product variant identifier
            - title (str): Product name/title with variant details
            - description (str): Detailed product description (may contain HTML)
            - image (str): URL to product image for display
            - price (Price): Product price with amount and currency_code
            Returns None if product is not found or not published
    
    Example AI Conversation Flow:
        User: "Tell me more about the wool sweater"
        AI: [calls get_product_details(handle="wool-sweater")]
        AI: "The Wool Sweater is a cozy winter essential. It's available in 
             3 sizes: Small ($45.99), Medium ($45.99), Large ($47.99). 
             It's made from 100% merino wool..."
    
    Example Usage:
        >>> # Get product by handle
        >>> product = get_product_details(handle="wool-sweater")
        >>> if product:
        ...     print(f"{product.title}: ${product.price.amount}")
        >>> 
        >>> # Get product by ID (from search results)
        >>> product = get_product_details(product_id="gid://shopify/ProductVariant/123")
        >>> if product:
        ...     print(f"Description: {product.description}")
    
    Note:
        - Provide either product_id OR handle, not both
        - If both are provided, product_id takes precedence
        - Product must be published to be retrievable
        - Pricing may vary by region/market
        - Returns None if product doesn't exist or isn't published
    """
    logger.info(f"get_product_details called with product_id: '{product_id}'")
    
    try:
        logger.info("Sending get product request to storefront client")
        resp = storefront_client.get_product(GetProductRequest(id=product_id))
        
        if resp.product is None:
            logger.info(f"Product not found: {product_id}")
            return None
        
        logger.info(f"Received product: {resp.product.title}")
        
        # Convert the client Product type to the tool Product type
        # Take the first variant as the primary product representation
        if not resp.product.variants:
            logger.warning(f"Product {resp.product.title} has no variants")
            return None
        
        # Return the first variant as a Product
        first_variant = resp.product.variants[0]
        product = Product(
            id=first_variant.id,
            title=f"{resp.product.title} - {first_variant.title}",
            description=resp.product.description,
            image=resp.product.images[0] if resp.product.images else "",
            price=Price(
                amount=first_variant.price.amount,
                currency_code=first_variant.price.currency_code,
            ),
        )
        
        logger.info(f"Successfully retrieved product: {product.title}")
        return product
    
    except Exception as e:
        logger.error(f"Error in get_product_details: {str(e)}", exc_info=True)
        return None
