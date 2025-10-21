import logging
import sys

from agent.backend.types.types import CartWidget, ProductWidget, Widget, WidgetType


# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def create_products_widgets(prod_list: list[dict]) -> list[Widget]:
    ws = []
    for prod in prod_list:
        logger.debug(f"Creating product widget for: {prod.get('title', 'Unknown product')}")
        ws.append(ProductWidget(
            type=WidgetType.PRODUCT,
            data={
                "id": prod.get("id"),
                "title": prod.get("title"),
                "description": prod.get("description"),
                "price": prod.get("price", {}).get("amount"),
                "currency": prod.get("price", {}).get("currency_code"),
                "image_url": prod.get("image_url"),
            },
        ))
        logger.debug(f"Product widget created: {prod.get('title')} - {prod.get('price', {}).get('amount')} {prod.get('price', {}).get('currency_code')}")

    return ws

def create_cart_widget(cart: dict) -> Widget:
    logger.debug("Creating cart widget")
    subtotal = cart.get("subtotal_amount", {})
    tax = cart.get("tax_amount", {}) or {}
    total = cart.get("total_amount", {})
    
    logger.debug(f"Cart details - Subtotal: {subtotal.get('amount')} {subtotal.get('currency_code')}, " +
                f"Tax: {tax.get('amount')} {tax.get('currency_code')}, " +
                f"Total: {total.get('amount')} {total.get('currency_code')}")
    
    widget = CartWidget(
        type=WidgetType.CART,
        data={
            "checkout_url": cart.get("checkout_url"),
            "subtotal_amount": subtotal.get("amount"),
            "subtotal_amount_currency_code": subtotal.get("currency_code"),
            "tax_amount": tax.get("amount"),
            "tax_amount_currency_code": tax.get("currency_code"),
            "total_amount": total.get("amount"),
            "total_amount_currency_code": total.get("currency_code"),
        },
    )
    logger.debug("Cart widget created successfully")
    return widget
