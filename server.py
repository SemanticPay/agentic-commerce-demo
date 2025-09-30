from flask import Flask, request, jsonify
from base_types import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    Cart,
    CheckoutSession,
    SearchRequest,
)
from utils import (
    calculate_cart_final_price,
    get_unique_checkout_session_id,
    get_items_by_filters,
    get_items_by_ids
)

app = Flask(__name__)


@app.route('/api/checkout_sessions', methods=['POST'])
def checkout_sessions():
    """
    Checkout session endpoint that processes a cart and buyer information.
    Expects a JSON body with 'cart' and 'buyer' fields.
    """
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid JSON body"}), 400
        req = CheckoutSessionRequest(**data)
        
        items = get_items_by_ids(req.item_ids)
        cart = Cart(items=items, final_price=calculate_cart_final_price(items, req.buyer))
        # TODO: create DB entries for these and get the ID for free
        checkout_session = CheckoutSession(id=get_unique_checkout_session_id(), cart=cart, buyer=req.buyer)

        resp = CheckoutSessionResponse(checkout_session=checkout_session)
        # Ensure JSON-serializable output
        return jsonify(resp.model_dump())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search():
    """
    Search endpoint that filters items based on keywords in their title.
    Accepts 'query' and 'keywords' parameters.
    """
    try:
        # Get parameters from request
        req = SearchRequest(**request.args)
        items = get_items_by_filters(req.query, req.keywords)
        # Convert Pydantic models to dicts for JSON response
        return jsonify([item.model_dump() for item in items])

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    print("Starting Simple Search Server...")
    print("  GET/POST /api/search - Search items")
    app.run(debug=True, host='0.0.0.0', port=5000)
