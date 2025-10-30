import logging
import os
import sys


from google.adk.tools import ToolContext

from agent.backend.state import keys
from agent.backend.client.base_types import Address, AddressOption, CartAddressInput, CartCreateRequest, CartGetRequest, CartLineInput, StoreProvider
from agent.backend.client.factory import get_storefront_client
from agent.backend.client.interface import StoreFrontClient
from agent.backend.types.types import Cart, Price


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
    title: str = "",
    description: str = "",
    image_url: str = "",
    price: float = None,
    tool_context: ToolContext = None,
) -> None:
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    cart = tool_context.state.get(keys.CART_STATE_KEY, {})
    details = cart.get(item_id, {
        "quantity": 0,
        "title": title,
        "description": description,
        "image_url": image_url,
        "price": price,
    })
    details["quantity"] = details["quantity"] + quantity
    cart[item_id] = details

    tool_context.state[keys.CART_STATE_KEY] = cart
    logger.info(f"Added item {item_id} (qty: {quantity})")


def remove_item_from_cart(
    item_id: str,
    tool_context: ToolContext,
) -> None:
    if item_id in tool_context.state.get(keys.CART_STATE_KEY, {}):
        del tool_context.state[keys.CART_STATE_KEY][item_id]
        logger.info(f"Removed item {item_id}.")
        return

    logger.info("Item not found in cart; nothing to remove")


def create_shopify_cart_and_get_checkout_url(
    tool_context: ToolContext,
) -> None:
    logger.info("create_shopify_cart_and_get_checkout_url called")

    state_cart: dict[str, int] = tool_context.state.get(keys.CART_STATE_KEY, {})
    if not state_cart:
        raise Exception("No items in state_cart to create")

    logger.info(f"Items requested: {len(state_cart)} product(s)")
    
    try:
        logger.info("Building state_cart line items")
        lines = []
        for item_id, quantity in state_cart.items():
            lines.append(CartLineInput(
                quantity=quantity,
                merchandiseId=item_id,
            ))
            logger.debug(f"Added line item: {item_id} (qty: {quantity})")
        logger.info(f"Created {len(lines)} cart line item(s)")

        logger.info("Sending cart creation request to storefront client")
        resp = storefront_client.cart_create(req=CartCreateRequest(
            lines=lines,
        ))
        logger.info("Cart created successfully on storefront")

        if resp.user_errors:
            raise Exception(f"User errors during cart creation: {resp.user_errors}")

        if resp.warnings:
            logger.warning(f"Warnings during cart creation: {resp.warnings}")

        if not resp.cart:
            raise Exception("No cart data returned from storefront")

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
        tool_context.state[keys.SHOPIFY_CART] = cart
    
    except Exception as e:
        logger.error(f"Error in create_shopify_cart_and_get_checkout_url: {str(e)}", exc_info=True)
        raise

# def cart_get(cart_id: str, tool_context: ToolContext) -> Cart:
#     """Retrieve an existing shopping cart by its unique identifier.
    
#     This MCP tool allows AI agents to fetch the current state of a previously
#     created cart, including all items, quantities, and pricing information.
#     Useful for resuming shopping sessions or checking cart status.
    
#     **AI Agent Instructions:**
#     - Use this tool to retrieve a cart that was created earlier
#     - The cart_id comes from the cart returned by cart_create()
#     - Carts may expire after inactivity (typically 10-30 days)
#     - If cart is not found, it may have expired - create a new one
#     - Use this to show the user their current cart contents
#     - Prices may have changed since cart creation
    
#     **Common Use Cases:**
#     1. User says "What's in my cart?" or "Show my cart"
#     2. Resuming a previous shopping session
#     3. Verifying cart contents before directing to checkout
#     4. Checking updated prices or availability
    
#     Args:
#         cart_id (str): The unique cart identifier returned from cart_create().
#             Format is platform-specific.
#             Example: "gid://shopify/Cart/abc123def456"
    
#     Returns:
#         Cart: Cart object containing:
#             - checkout_url (str): URL to complete checkout
#             - subtotal_amount (Price): Cart subtotal before tax
#             - tax_amount (Price | None): Tax amount if calculated
#             - total_amount (Price): Final total amount
    
#     Example AI Conversation Flow:
#         User: "What's in my cart?"
#         AI: [calls cart_get(cart_id="gid://shopify/Cart/abc123")]
#         AI: "Your cart total is $91.98 (subtotal: $85.00, tax: $6.98).
#              Ready to checkout? Here's your link: [checkout_url]"
        
#         User: "Can you check my cart from earlier?"
#         AI: [calls cart_get with saved cart_id]
#         AI: [if error] "I couldn't find that cart - it may have expired.
#              Would you like to create a new one?"
    
#     Example Usage:
#         >>> # Get a cart by ID
#         >>> cart = cart_get(cart_id="gid://shopify/Cart/abc123")
#         >>> print(f"Subtotal: ${cart.subtotal_amount.amount}")
#         >>> print(f"Tax: ${cart.tax_amount.amount if cart.tax_amount else 0}")
#         >>> print(f"Total: ${cart.total_amount.amount}")
#         >>> print(f"Checkout: {cart.checkout_url}")
    
#     Raises:
#         Exception: If cart retrieval fails due to:
#             - Cart not found (invalid or expired ID)
#             - Network/API errors
#             - Invalid cart_id format
    
#     Note:
#         - Cart IDs are temporary and expire after inactivity
#         - Prices may change between creation and retrieval
#         - Out-of-stock items may be removed automatically by some platforms
#         - The checkout URL remains valid as long as the cart exists
#         - Some platforms may update tax calculations when retrieving cart
#     """
#     logger.info(f"cart_get called with cart_id: {cart_id}")
    
#     try:
#         logger.info("Sending cart retrieval request to storefront client")
#         resp = storefront_client.cart_get(req=CartGetRequest(id=cart_id))
#         logger.info("Cart retrieved successfully from storefront")

#         logger.info("Building cart response object")
#         cart = Cart(
#             checkout_url=resp.cart.checkout_url, 
#             subtotal_amount=Price(
#                 amount=resp.cart.cost.subtotal_amount.amount,
#                 currency_code=resp.cart.cost.subtotal_amount.currency_code,
#             ),
#             tax_amount=Price(
#                 amount=resp.cart.cost.total_tax_amount.amount,
#                 currency_code=resp.cart.cost.total_tax_amount.currency_code,
#             ) if resp.cart.cost.total_tax_amount else None,
#             total_amount=Price(
#                 amount=resp.cart.cost.total_amount.amount,
#                 currency_code=resp.cart.cost.total_amount.currency_code,
#             ),
#         )
        
#         logger.info(f"Cart retrieved - Subtotal: {cart.subtotal_amount.amount} {cart.subtotal_amount.currency_code}")
#         if cart.tax_amount:
#             logger.info(f"Tax: {cart.tax_amount.amount} {cart.tax_amount.currency_code}")
#         logger.info(f"Total: {cart.total_amount.amount} {cart.total_amount.currency_code}")
#         logger.info(f"Checkout URL: {cart.checkout_url}")

#         return cart
    
#     except Exception as e:
#         logger.error(f"Error in cart_get: {str(e)}", exc_info=True)
#         raise
