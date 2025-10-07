from fastmcp import FastMCP
from datetime import datetime
from base_types import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    Cart,
    CheckoutSession,
    DelegatePaymentRequest,
    DelegatePaymentResponse,
    FullfillmentAddress,
    SearchRequest,
    Item,
    Buyer,
    Order,
)
from mcp_server.widgets import ItemWidget
from utils import (
    calculate_cart_final_price,
    get_unique_checkout_session_id,
    get_items_by_filters,
    get_items_by_ids,
    handle_payment,
)

# Initialize FastMCP server
mcp = FastMCP("SemanticPay Shopping Server")

# In-memory storage for orders
orders_storage: dict[str, Order] = {}


@mcp.tool()
def create_checkout_session(
    item_ids: list[str], buyer: Buyer, fullfillment_address: FullfillmentAddress
) -> CheckoutSessionResponse:
    """
    Create a checkout session that processes a cart and buyer information.

    Args:
        item_ids: List of item IDs to include in the cart
        buyer: Buyer information including name, email, phone, and country

    Returns:
        CheckoutSessionResponse containing the checkout session with cart and buyer details
    """
    req = CheckoutSessionRequest(
        item_ids=item_ids, buyer=buyer, fullfillment_address=fullfillment_address
    )

    items = get_items_by_ids(req.item_ids)
    cart = Cart(
        items=items,
        final_price=calculate_cart_final_price(items, req.fullfillment_address),
    )
    checkout_session_id = get_unique_checkout_session_id()
    checkout_session = CheckoutSession(
        id=checkout_session_id,
        cart=cart,
        fullfillment_address=req.fullfillment_address,
        buyer=req.buyer,
    )

    # Create Order object with status "waiting_for_payment"
    current_time = datetime.now().isoformat()
    order = Order(
        checkout_session_id=checkout_session_id,
        items=items,
        buyer=req.buyer,
        fullfillment_address=req.fullfillment_address,
        status="waiting_for_payment",
        created_at=current_time,
        updated_at=current_time,
    )

    # Store the order in memory
    orders_storage[checkout_session_id] = order

    resp = CheckoutSessionResponse(checkout_session=checkout_session)
    return resp


@mcp.tool()
def search_items(query: str = "", keywords: str = "") -> list[ItemWidget]:
    """
    Search for items based on query and keywords in their title.

    Args:
        query: Search query string (optional)
        keywords: Additional keywords to search for (optional)

    Returns:
        List of item widgets matching the search criteria
    """
    req = SearchRequest(query=query, keywords=keywords)
    items = get_items_by_filters(req.query, req.keywords)

    widgets: list[ItemWidget] = []
    for item in items:
        widget = ItemWidget(data=item)
        widgets.append(widget) 

    return widgets


@mcp.tool()
def delegate_payment(request: DelegatePaymentRequest) -> DelegatePaymentResponse:
    """
    Delegate payment processing for a checkout session.

    Args:
        request: DelegatePaymentRequest containing payment_method, allowance, and billing_address

    Returns:
        DelegatePaymentResponse indicating success or failure with optional message
    """
    try:
        handle_payment(
            request.payment_method, request.allowance, request.billing_address
        )

        # If payment is successful, update the order status to "done"
        checkout_session_id = request.allowance.checkout_session_id
        if checkout_session_id in orders_storage:
            order = orders_storage[checkout_session_id]
            order.status = "done"
            order.updated_at = datetime.now().isoformat()
            orders_storage[checkout_session_id] = order

        resp = DelegatePaymentResponse(success=True)
        return resp

    except Exception as e:
        resp = DelegatePaymentResponse(success=False, message=str(e))
        return resp


if __name__ == "__main__":
    print("Starting SemanticPay MCP Server...")
    print("Available tools:")
    print("  - create_checkout_session: Create a new checkout session")
    print("  - search_items: Search for items by query and keywords")
    print("  - delegate_payment: Process payment delegation")
    print("Running as HTTP server on http://localhost:8000")
    mcp.run(transport="http", host="0.0.0.0", port=8000)
