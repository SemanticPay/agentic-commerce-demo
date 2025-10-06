import uuid
from base_types import FullfillmentAddress, Item, Buyer
from items import ITEMS


def calculate_cart_final_price(
    items: list[Item], fullfillment_address: FullfillmentAddress
) -> float:
    """
    Calculate the final price of the cart.
    For simplicity, this example just sums up item prices.
    """
    shipping_cost = calculate_cart_shipping_price(items, fullfillment_address)
    total = sum(item.price for item in items) + shipping_cost
    return total


def calculate_cart_shipping_price(
    items: list[Item], fullfillment_address: FullfillmentAddress
) -> float:
    """
    Calculate shipping price based on buyer's location.
    For simplicity, this example returns a flat rate.
    """
    if fullfillment_address.country.lower() == "usa":
        return 5.00
    else:
        return 15.00  # Higher shipping fee for international orders


# TODO: should be removed after using a DB
def get_unique_checkout_session_id() -> str:
    """
    Generate a unique checkout session ID.
    In a real application, this would be more robust.
    """
    return str(uuid.uuid4())


def get_items_by_filters(query: str, keywords: str) -> list[Item]:
    search_terms = f"{query} {keywords}".strip().lower()
    search_words = search_terms.split()
    filtered_items = []

    for item in ITEMS:
        title_lower = item.title.lower()
        # Check if any search word is in the title
        if any(word in title_lower for word in search_words):
            filtered_items.append(item)

    return filtered_items


def get_items_by_ids(item_ids: list[str]) -> list[Item]:
    id_set = set(int(i) for i in item_ids)
    return [item for item in ITEMS if item.id in id_set]


def handle_payment(payment_method, allowance, billing_address):
    """
    Stub function to handle payment delegation.
    In a real application, this would interact with a payment gateway.
    """
    print(
        f"Delegating payment of {allowance.amount} {allowance.currency} for session {allowance.checkout_session_id}"
    )
    print(
        f"Using payment method: {payment_method.type}, card ending in {payment_method.number[-4:]}"
    )
    print(
        f"Billing address: {billing_address.line_one}, {billing_address.city}, {billing_address.country}"
    )
    # Simulate successful payment delegation
    return True
