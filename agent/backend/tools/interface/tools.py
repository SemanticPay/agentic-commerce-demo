import logging
import sys
from google.adk.tools import ToolContext
from agent.backend.state import keys
from agent.backend.types.types import (
    Cart,
    CartWidget,
    Product,
    ProductSection,
    ProductWidget,
    StateCart,
    Widget,
    WidgetType,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
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
    product_cards_html = ""

    for prod in prod_list:
        logger.debug(f"Creating product widget for: {prod.title}")
        card_html = f"""
        <div class="w-full bg-white rounded-2xl overflow-hidden border border-gray-100 transition-all duration-300 flex flex-col h-full">
            <img 
                src="{prod.image}" 
                alt="{prod.title}" 
                class="w-full h-48 object-cover flex-shrink-0"
            />
            <div class="p-6 flex flex-col flex-grow">
                <div class="flex-grow mb-4">
                    <h3 class="text-black mb-2">{prod.title}</h3>
                    <p class="text-gray-600 text-[14px] leading-relaxed">
                        {prod.description}
                    </p>
                    <p class="text-black font-semibold mt-2">
                        {formatPrice(prod.price.amount, prod.price.currency_code)}
                    </p>
                </div>
                <div class="flex gap-3">
                    <button 
                        class="add-to-cart-btn flex-1 bg-white text-black border border-gray-200 hover:bg-gray-50 hover:shadow-md hover:scale-[1.02] cursor-pointer transition-all duration-200 rounded-xl h-11 flex items-center justify-center"
                        data-title="{prod.title}"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13l-1.3 5H18a1 1 0 001-1v-1M7 13L5.4 5M16 21a1 1 0 100-2 1 1 0 000 2zm-8 0a1 1 0 100-2 1 1 0 000 2z"/>
                        </svg>
                        Add to Cart
                    </button>
                </div>
            </div>
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
            raw_html_string=card_html,
        ))
        product_cards_html += f"<div class='w-[30%]'>{card_html}</div>\n"

    container_html = f"""
    <div class="bg-white flex flex-wrap justify-start gap-6 w-full p-8 rounded-3xl">
        {product_cards_html}
    </div>
    """

    return [Widget(
        type=WidgetType.PRODUCT_SECTIONS,
        data={"products": [p.model_dump() for p in prod_list]},
        raw_html_string=container_html,
    )]


def create_cart_widget(tool_context: ToolContext) -> Widget:
    store_cart_data: Cart = tool_context.state.get(keys.STORE_CART, {})
    store_cart = Cart(**store_cart_data) if store_cart_data else None  # type: ignore
    state_cart_data = tool_context.state.get(keys.CART_STATE_KEY, {})
    state_cart: StateCart = StateCart(**state_cart_data) if state_cart_data else StateCart()

    if not store_cart:
        if not state_cart or not state_cart.id_to_product:
            return Widget(
                type=WidgetType.CART,
                data={},
                raw_html_string="<p>Your cart is empty.</p>",
            )

    subtotal = store_cart.subtotal_amount  # type: ignore
    tax = store_cart.tax_amount  # type: ignore
    total = store_cart.total_amount  # type: ignore
    checkout_url = store_cart.checkout_url  # type: ignore

    cart_products_html = ""
    for product in state_cart.id_to_product.values():
        cart_products_html += f"""
        <div class="flex justify-between items-center border-b border-gray-100 py-3">
            <div>
                <h4 class="text-black text-[15px] font-medium">{product.title}</h4>
                <p class="text-gray-600 text-[13px]">Qty: {product.quantity}</p>
            </div>
            <p class="text-black font-semibold text-[14px]">
                {formatPrice(product.price.amount * product.quantity, product.price.currency_code)}
            </p>
        </div>
        """

    html_string = f"""
    <div class="bg-white w-full max-w-2xl mx-auto rounded-2xl">
        <div class="mb-6">
            <h3 class="text-black text-[22px] font-semibold mb-2">Cart Summary</h3>
            <p class="text-gray-600 text-[14px]">Review your selected items</p>
        </div>

        <div class="divide-y divide-gray-100 mb-6">
            {cart_products_html}
        </div>

        <div class="space-y-2 border-t border-gray-200 pt-4">
            <div class="flex justify-between text-[14px]">
                <span class="text-gray-600">Subtotal:</span>
                <span class="text-black font-medium">{formatPrice(subtotal.amount, subtotal.currency_code)}</span>
            </div>
            <div class="flex justify-between text-[14px]">
                <span class="text-gray-600">Tax:</span>
                <span class="text-black font-medium">{formatPrice((tax.amount if tax else 0), (tax.currency_code if tax else subtotal.currency_code))}</span>
            </div>
            <div class="flex justify-between text-[15px] font-semibold border-t border-gray-300 pt-3">
                <span>Total:</span>
                <span>{formatPrice(total.amount, total.currency_code)}</span>
            </div>
        </div>

        <div class="flex justify-center mt-8">
            <a href="{checkout_url}" target="_blank" rel="noopener noreferrer"
                class="bg-black text-white px-8 py-3 rounded-full hover:bg-gray-800 transition-all duration-200">
                Proceed to Checkout
            </a>
        </div>
    </div>
    """

    return CartWidget(
        type=WidgetType.CART,
        data={
            "checkout_url": checkout_url,
            "subtotal_amount": subtotal.amount,
            "subtotal_amount_currency_code": subtotal.currency_code,
            "tax_amount": tax.amount if tax else 0,
            "tax_amount_currency_code": tax.currency_code if tax else subtotal.currency_code,
            "total_amount": total.amount,
            "total_amount_currency_code": total.currency_code,
        },
        raw_html_string=html_string,
    )


def formatPrice(amount: float, currency_code: str) -> str:
    if currency_code == "USD":
        return f"${amount:,.2f}"
    elif currency_code == "EUR":
        return f"€{amount:,.2f}"
    elif currency_code == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency_code}"
