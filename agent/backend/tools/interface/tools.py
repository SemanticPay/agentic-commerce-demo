import logging
import sys
from typing import Any

from google.adk.tools import ToolContext

from agent.backend.state import keys
from agent.backend.types.types import Cart, CartWidget, Product, ProductSection, ProductWidget, StateCart, Widget, WidgetType


# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def create_products_section_widget(tool_context: ToolContext) -> Widget:
    sections: list[ProductSection] = tool_context.state.get(keys.PRODUCT_SECTIONS_STATE_KEY, [])
    if len(sections) == 0:
        logger.error("No product sections found in state")
        return Widget(
            type=WidgetType.PRODUCT_SECTIONS,
            data={"sections": []},
            raw_html_string="<p>No product sections available.</p>"
        )

    sections_widget_html = ""
    for sec in sections:
        sections_widget_html += f"<h2>{sec.title or "EMPTY"}</h2>\n"
        sections_widget_html += f"<h3>{sec.subtitle or "EMPTY"}</h3>\n"
        sections_widget_html += f"<p>{sec.description or "EMPTY"}</p>\n"
        sections_widget_html += "<div class='product-section'>\n"
        raw_products = [prod.model_dump() for prod in sec.products]
        prods_widgets = create_products_widgets(raw_products, tool_context)
        for pw in prods_widgets:
            sections_widget_html += pw.raw_html_string + "\n"
        sections_widget_html += "</div>\n"

    return Widget(
        type=WidgetType.PRODUCT_SECTIONS,
        data={
            "sections": [sec.model_dump() for sec in sections]
        },
        raw_html_string=sections_widget_html
    )


def create_products_widgets(raw_prod_list: list[dict], tool_context: ToolContext) -> list[Widget]:
    prod_list = [Product(**prod) for prod in raw_prod_list]
    ws = []

    for prod in prod_list:
        logger.debug(f"Creating product widget for: {prod.title}")

        html_string = f"""
        <div className="product-image-container">
            <img 
                src={prod.image} 
                alt={prod.title}
                className="product-image"
            />
        </div>
        <div className="product-details">
            <h3 className="product-title">{prod.title}</h3>
            <p className="product-description">{prod.description}</p>
            <p className="product-price">
                {formatPrice(prod.price.amount, prod.price.currency_code)}
            </p>
        </div>
        """

        ws.append(ProductWidget(
            type=WidgetType.PRODUCT,
            data={
                "id": prod.id,
                "title": prod.title,
                "description": prod.description,
                "price": prod.price.amount,
                "currency": prod.price.currency_code,
                "image": prod.image,
            },
            raw_html_string=html_string
        ))
        logger.debug(f"Product widget created: {prod.title} - {prod.price.amount} {prod.price.currency_code}")

    return ws

def create_cart_widget(tool_context: ToolContext) -> Widget:
    store_cart_data: Cart = tool_context.state.get(keys.STORE_CART, {})
    store_cart = Cart(**store_cart_data) if store_cart_data else None
    state_cart_data = tool_context.state.get(keys.CART_STATE_KEY, {})
    state_cart: StateCart = StateCart(**state_cart_data) if state_cart_data else StateCart()

    if store_cart is None:
        logger.info("No store cart found in state; cannot create cart widget")
        if state_cart is None or len(state_cart.id_to_product.keys()) == 0:
            logger.error("State cart is also empty; cannot create cart widget")
            return Widget(
                type=WidgetType.CART,
                data={},
                raw_html_string="<p>Your cart is empty.</p>"
            )
        else:
            logger.error("State cart has items but no store cart; cannot create cart widget")
            return Widget(
                type=WidgetType.CART,
                data={},
                raw_html_string="<p>Your cart is empty.</p>"
            )


    logger.info(f"Creating cart widget from state cart: {store_cart}")

    logger.debug("Creating cart widget")
    subtotal = store_cart.subtotal_amount
    tax = store_cart.tax_amount
    total = store_cart.total_amount
    
    logger.debug(f"Cart details - Subtotal: {subtotal.amount} {subtotal.currency_code}, " +
                f"Tax: {tax.amount if tax else 0} {tax.currency_code if tax else 0}, " +
                f"Total: {total.amount} {total.currency_code}")

    # TODO: Retrieve line items from store cart instead of using state cart, as these two can be out of sync
    cart_products_html = ""
    for product in state_cart.id_to_product.values():
        cart_products_html += f"""
        <div class="cart-product-item">
            <span class="cart-product-title">{product.title}</span>
            <span class="cart-product-quantity">Qty: {product.quantity}</span>
            <span class="cart-product-price">
                {formatPrice(product.price.amount * product.quantity, product.price.currency_code)}
            </span>
        </div>
        """

    html_string = f"""
    <div class="cart-header">
        <h3>Cart Summary</h3>
    </div>
    <div class="cart-details">
        <div class="cart-products">
            {cart_products_html}
        </div>
        <div class="cart-line-item">
            <span class="cart-label">Subtotal:</span>
            <span class="cart-value">
                {formatPrice(subtotal.amount, subtotal.currency_code)}
            </span>
        </div>
        <div class="cart-line-item">
            <span class="cart-label">Tax:</span>
            <span class="cart-value">
                {formatPrice((tax.amount if tax else 0), (tax.currency_code if tax else subtotal.currency_code))}
            </span>
        </div>
        <div class="cart-line-item cart-total">
            <span class="cart-label">Total:</span>
            <span class="cart-value">
                {formatPrice(total.amount, total.currency_code)}
            </span>
        </div>
    </div>
    <div class="cart-actions">
        <a 
        href={store_cart.checkout_url} 
        target="_blank" 
        rel="noopener noreferrer"
        class="checkout-button"
        >
            Proceed to Checkout
        </a>
    </div>
    """
    
    widget = CartWidget(
        type=WidgetType.CART,
        data={
            "checkout_url": store_cart.checkout_url,
            "subtotal_amount": subtotal.amount,
            "subtotal_amount_currency_code": subtotal.currency_code,
            "tax_amount": tax.amount if tax else 0,
            "tax_amount_currency_code": tax.currency_code if tax else subtotal.currency_code,
            "total_amount": total.amount,
            "total_amount_currency_code": total.currency_code,
        },
        raw_html_string=html_string
    )
    logger.debug("Cart widget created successfully")
    return widget


def formatPrice(amount: float, currency_code: str) -> str:
    """Formats the price based on currency code."""
    if currency_code == "USD":
        return f"${amount:,.2f}"
    elif currency_code == "EUR":
        return f"€{amount:,.2f}"
    elif currency_code == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency_code}"
