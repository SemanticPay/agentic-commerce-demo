import logging
import sys
from typing import Any

from google.adk.tools import ToolContext

from agent.backend.state import keys
from agent.backend.types.types import Cart, CartWidget, Product, ProductWidget, ProductSection, Widget, WidgetType


# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def create_products_widgets(raw_prod_list: list[dict], tool_context: ToolContext) -> list[Widget]:
    prod_list = [Product(**prod) for prod in raw_prod_list]
    ws = []

    product_cards_html = ""
    for prod in prod_list:
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
            raw_html_string=card_html
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
        raw_html_string=container_html
    )]

def create_cart_widget(tool_context: ToolContext) -> Widget:
    internal_cart = tool_context.state.get(keys.CART_STATE_KEY, {})
    shopify_cart = tool_context.state.get(keys.SHOPIFY_CART, None)

    logger.info(f"Rendering cart widget with {len(internal_cart)} internal items")
    checkout_url = getattr(shopify_cart, "checkout_url", "#")

    # If empty
    if not internal_cart:
        html_string = """
        <div class="bg-white w-full max-w-3xl mx-auto rounded-2xl p-8">
            <h1 class="text-black text-[22px] font-semibold mb-4">Your Cart</h1>
            <p class="text-gray-500 text-[14px] italic">Your cart is empty.</p>
        </div>
        """
        return CartWidget(
            type=WidgetType.CART,
            data={"checkout_url": checkout_url},
            raw_html_string=html_string,
        )

    # Render internal items (only id + quantity available)
    items_html = ""
    for item_id, qty in internal_cart.items():
        items_html += f"""
        <div class="flex gap-3 bg-white border border-gray-100 rounded-xl p-3 w-full">
            <div class="flex flex-col justify-between flex-grow">
                <div>
                    <h3 class="text-black text-[14px] leading-tight">Item: {item_id}</h3>
                    <p class="text-gray-600 text-[12px] leading-snug">Quantity: {qty}</p>
                </div>
            </div>
        </div>
        """

    html_string = f"""
    <div class="bg-white w-full max-w-3xl mx-auto rounded-2xl p-8">
        <div class="mb-6">
            <h1 class="text-black text-[22px] font-semibold mb-1">Your Cart</h1>
            <p class="text-gray-600 text-[14px]">Items ready for checkout</p>
        </div>

        <div class="space-y-3 mb-8">
            {items_html}
        </div>

        <div class="flex">
            <a
                href="{checkout_url}"
                target="_blank"
                rel="noopener noreferrer"
                class="flex-1 bg-black text-white hover:bg-gray-800 cursor-pointer transition-all duration-200 rounded-xl h-12 flex items-center justify-center gap-2"
            >
                Proceed to Checkout
            </a>
        </div>
    </div>
    """

    return CartWidget(
        type=WidgetType.CART,
        data={
            "checkout_url": checkout_url,
            "internal_items": internal_cart,
        },
        raw_html_string=html_string,
    )

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
