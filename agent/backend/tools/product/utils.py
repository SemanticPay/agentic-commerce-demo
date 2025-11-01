import logging
import sys
from agent.backend.client.base_types import SearchProductsRequest
from agent.backend.client.interface import StoreFrontClient
from agent.backend.types.types import Price, Product, ProductList

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def _search_products(query: str, client: StoreFrontClient) -> ProductList:
    logger.info(f"_search_products called with query: '{query}'")
    
    try:
        logger.info("Sending search request to storefront client")
        resp = client.search_products(SearchProductsRequest(query=query))
        logger.info(f"Received response with {len(resp.products)} products")

        prod_list = ProductList()
        logger.info("Processing products and variants")
        
        for idx, prod in enumerate(resp.products):
            logger.debug(f"Processing product {idx + 1}/{len(resp.products)}: {prod.title}")
            for variant_idx, variant in enumerate(prod.variants):
                product = Product(
                    id=prod.id,
                    variant_id=prod.variants[0].id if prod.variants else "",
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
        logger.error(f"Error in _search_products: {str(e)}", exc_info=True)
        return ProductList()
