import logging
import os
import sys
from typing import Optional

from google.adk.tools import ToolContext

from agent.backend.client.base_types import GetProductRequest, StoreProvider
from agent.backend.tools.product.utils import _search_products
from agent.backend.client.factory import get_storefront_client
from agent.backend.client.interface import StoreFrontClient
from agent.backend.state import keys
from agent.backend.tools.context.utils import get_search_categories, get_search_query
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
    categories = get_search_categories(tool_context.state)

    sections: list[ProductSection] = []
    for cat in categories:
        query = cat.query
        prod_list = _search_products(query, storefront_client)
        sections.append(ProductSection(
            title=cat.title,
            description=cat.description,
            subtitle=cat.subtitle,
            products=prod_list.products,
        ))

    logger.info(f"Setting product categories sections in state: {sections}")
    tool_context.state[keys.PRODUCT_SECTIONS_STATE_KEY] = sections


def search_products(tool_context: ToolContext) -> ProductList:
    query = get_search_query(tool_context.state)

    logger.info(f"search_products called with query: '{query}'")
    
    try:
        prod_list = _search_products(query, storefront_client) 
        return prod_list
    
    except Exception as e:
        logger.error(f"Error in search_products: {str(e)}", exc_info=True)
        return ProductList()


def get_product_details(product_id: str, tool_context: Optional[ToolContext] = None) -> Optional[Product]:
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
        product = Product(
            id=resp.product.id,
            variant_id=resp.product.variants[0].id if resp.product.variants else "",
            title=resp.product.title,
            description=resp.product.description,
            image=resp.product.images[0] if resp.product.images else "",
            price=Price(
                amount=resp.product.price.amount,
                currency_code=resp.product.price.currency_code,
            ),
        )
        
        logger.info(f"Successfully retrieved product: {product.title}")
        return product
    
    except Exception as e:
        logger.error(f"Error in get_product_details: {str(e)}", exc_info=True)
        return None
