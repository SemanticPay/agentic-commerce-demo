import logging
import os
import sys
from typing import Optional


from google.adk.tools import ToolContext

from agent.backend.state import keys
from agent.backend.client.base_types import  CartCreateRequest, CartLineInput, GetProductRequest, StoreProvider
from agent.backend.client.factory import get_storefront_client
from agent.backend.client.interface import StoreFrontClient
from agent.backend.types.types import Cart, Price, StateCart, StateCartProduct


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
    store_url=os.getenv("SHOPIFY_STOREFRONT_STORE_URL", ""),
)
logger.info("Storefront client initialized successfully")


def add_item_to_cart(
    item_id: str,
    quantity: int,
    tool_context: ToolContext,
) -> None:
    if quantity <= 0:
        logger.error(f"Invalid quantity {quantity} for item ID {item_id}")
        return

    state_cart: StateCart = tool_context.state.get(keys.CART_STATE_KEY, StateCart())

    cart_product: StateCartProduct = state_cart.id_to_product.get(item_id) # type: ignore
    if cart_product is None:
        logger.info(f"Fetching product details for item ID: {item_id}")
        resp = storefront_client.get_product(req=GetProductRequest(id=item_id))
        if resp.product is None:
            logger.error(f"Product with ID {item_id} not found in store")
            return

        cart_product = StateCartProduct(
            id=item_id,
            quantity=0,
            title=resp.product.title,
            description=resp.product.description,
            image_url=resp.product.images[0] if resp.product.images else "",
            price=Price(amount=resp.product.price.amount, currency_code=resp.product.price.currency_code), 
        )

    cart_product.quantity += quantity
    state_cart.id_to_product[item_id] = cart_product
    tool_context.state[keys.CART_STATE_KEY] = state_cart
    logger.info(f"Added item {item_id} to state cart (qty: {quantity})")


def remove_item_from_cart(
    item_id: str,
    tool_context: ToolContext,
) -> None:
    state_cart: StateCart = tool_context.state.get(keys.CART_STATE_KEY, StateCart())
    if item_id in state_cart.id_to_product:
        del state_cart.id_to_product[item_id]
        tool_context.state[keys.CART_STATE_KEY] = state_cart
        logger.info(f"Removed item {item_id} from state cart")
        return

    logger.info("Item not found in cart; nothing to remove")


def create_store_cart_and_get_checkout_url(
    tool_context: ToolContext,
) -> None:
    logger.info("create_store_cart_and_get_checkout_url called")

    state_cart: StateCart = tool_context.state.get(keys.CART_STATE_KEY, StateCart())
    if len(state_cart.id_to_product) == 0:
        logger.info("State cart is empty; no items to add to store cart")
        return

    logger.info(f"Items requested: {len(state_cart.id_to_product)} product(s)")
    
    try:
        logger.info("Building state_cart line items")
        lines = []
        for product in state_cart.id_to_product.values():
            lines.append(CartLineInput(
                quantity=product.quantity,
                merchandiseId=product.id,
            ))
            logger.debug(f"Added line item: {product.id} (qty: {product.quantity})")
        logger.info(f"Created {len(lines)} cart line item(s)")

        if len(lines) == 0:
            logger.info("No line items to add to cart. Aborting store cart creation.")
            return

        logger.info("Sending cart creation request to storefront client")
        resp = storefront_client.cart_create(req=CartCreateRequest(
            lines=lines,
        ))
        logger.info("Cart created successfully on storefront")

        if resp.user_errors:
            logger.error(f"User errors during cart creation: {resp.user_errors}")
            return
            

        if resp.warnings:
            logger.warning(f"Warnings during cart creation: {resp.warnings}")

        if not resp.cart:
            logger.error("No cart returned from storefront after creation")
            return

        logger.info("Building cart response object")
        cart = Cart(
            checkout_url=resp.cart.checkout_url, 
            subtotal_amount=Price(
                amount=resp.cart.cost.subtotal_amount.amount,
                currency_code=resp.cart.cost.subtotal_amount.currency_code,
            ),
            tax_amount=Price(
                amount=resp.cart.cost.total_tax_amount.amount,
                currency_code=resp.cart.cost.total_tax_amount.currency_code,
            ) if resp.cart.cost.total_tax_amount else None,
            total_amount=Price(
                amount=resp.cart.cost.total_amount.amount,
                currency_code=resp.cart.cost.total_amount.currency_code,
            ),
        )
        
        logger.info(f"Cart created - Subtotal: {cart.subtotal_amount.amount} {cart.subtotal_amount.currency_code}")
        if cart.tax_amount:
            logger.info(f"Tax: {cart.tax_amount.amount} {cart.tax_amount.currency_code}")
        logger.info(f"Total: {cart.total_amount.amount} {cart.total_amount.currency_code}")
        logger.info(f"Checkout URL: {cart.checkout_url}")

        logger.info(f"Setting cart in state")
        tool_context.state[keys.STORE_CART] = cart
    
    except Exception as e:
        logger.error(f"Error in create_shopify_cart_and_get_checkout_url: {str(e)}", exc_info=True)
        raise
