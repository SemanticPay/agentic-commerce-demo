import logging
import sys

from google.adk.tools import ToolContext

from agent.backend.client.base_types import SearchProductsRequest, StoreProvider
from agent.backend.client.factory import get_storefront_client
from agent.backend.client.interface import StoreFrontClient
from agent.backend.types.types import Price, Product, ProductList

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
    store_url="https://huescorner.myshopify.com/api/2025-10/graphql.json",
)
logger.info("Storefront client initialized successfully")


def search_products(query: str, tool_context: ToolContext) -> ProductList:
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
                - image_url (str): URL to product image for display
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
                    image_url=prod.images[0],
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
        raise
