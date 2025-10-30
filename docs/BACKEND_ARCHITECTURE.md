## Backend Architecture

This backend is a FastAPI service that orchestrates a set of AI agents (Google ADK) and commerce tools (Shopify Storefront/Admin) to answer user queries and return renderable widgets to the frontend.

### Core Responsibilities
- Provide a stateless HTTP entrypoint with session continuity via `session_id`.
- Run an orchestrator agent that delegates to sub-agents (context, discovery, cart, product_details).
- Execute tools to fetch data from Shopify, manage in-memory state, and assemble widget payloads.
- Return a compact `QueryResponse` containing a short answer and typed widgets for UI rendering.

### Key Modules
- `agent/backend/main.py`
  - FastAPI app, CORS.
  - Endpoint: `POST /query` → `QueryRequest` → `QueryResponse`.
  - Calls `agents.orchestrator.agent.call_agent(...)` and converts agent function payloads into `widgets` via `extract_widgets_from_function_payloads`.

- `agent/backend/agents/orchestrator/agent.py`
  - Builds the orchestrator `Agent` (model: `gemini-2.0-flash-lite`) with instruction from `prompt.py`.
  - Registers sub-agents: context, discovery, cart, product_details.
  - Uses `Runner`, `InMemorySessionService`, `InMemoryArtifactService` to manage sessions and streaming events.
  - `call_agent` streams events, concatenates text responses, and collects function responses into `FunctionPayload[]` (no silent fallbacks; errors are raised).

- Sub-agents
  - `agents/context/*`: clarify user needs; write `SearchCategory[]` to state.
  - `agents/discovery/*`: search catalog and create product section widgets.
  - `agents/cart/*`: mutate in-memory cart, create a Shopify cart and a cart widget on demand.
  - `agents/product_details/*`: fetch detailed info for a single product by ID.

- Tools (`agent/backend/tools/*`)
  - Context: `set_search_categories`, `get_search_categories` (reads/writes state keys).
  - Product: `search_products` (flattens variants) and `get_product_details` (first variant as UI product); `search_product_categories` composes sections.
  - Interface: `create_products_widgets`, `create_products_section_widget`, `create_cart_widget` (widgets carry `raw_html_string` and `data`).
  - Cart: `add_item_to_cart`, `remove_item_from_cart`, `create_shopify_cart_and_get_checkout_url` (consumes in-memory cart and persists summarized Shopify cart in state).

- Shopify Clients (`agent/backend/client/*`)
  - `base_types.py`: normalized platform models (prices, products, carts) with GraphQL aliasing.
  - `factory.py`: provider switch → Shopify Storefront/Admin.
  - `shopify.py`:
    - `ShopifyGraphQLClient` (Storefront): `search_products`, `cart_create`, `cart_get`, `get_product`.
    - `ShopifyAdminClient` (Admin): `get_products` with pagination.
    - Strict error handling: HTTP/GraphQL errors logged and raised.

- Types and State
  - `types/types.py`: API and UI models: `QueryRequest`, `QueryResponse`, `Widget`, `Product`, `Cart`, etc.
  - `state/keys.py`: constants for tool context state: `X-cart`, `X-search-categories`, `X-shopify-cart`, `X-product-sections`.

### Request Flow (Sequence)
1) Frontend `POST /query` with `{ question, session_id? }`.
2) Backend ensures a `session_id`, calls `call_agent` with a user message.
3) Orchestrator delegates:
   - Context agent may call `set_search_categories`.
   - Discovery agent may call `search_product_categories` → `create_products_section_widget`.
   - Cart agent may call `add_item_to_cart`/`remove_item_from_cart`; upon "show cart" or checkout intent, calls `create_shopify_cart_and_get_checkout_url` then `create_cart_widget`.
   - Product details agent may call `get_product_details`.
4) `call_agent` aggregates text and tool function results as `FunctionPayload[]`.
5) `main.extract_widgets_from_function_payloads` maps known tool names to widget outputs and returns `QueryResponse { response, widgets, session_id }`.

### Error Handling
- Environment is loaded via `dotenv`; missing/invalid API calls raise exceptions (no default/fallback behavior).
- Shopify client methods raise on HTTP errors, timeouts, or GraphQL errors.
- `/query` converts unhandled errors into `HTTPException(500)` with details and logs.

### Configuration
- Required env variables (examples):
  - `SHOPIFY_STOREFRONT_STORE_URL`
  - `SHOPIFY_STOREFRONT_ACCESS_TOKEN` (if required by the store)
  - `SHOPIFY_ADMIN_API_STORE_URL`, `SHOPIFY_ADMIN_API_ACCESS_TOKEN` (for Admin tests)

### Running
- Python 3.12+
- Create and activate venv; install `requirements.txt`.
- Start API: `make agent-backend` (runs Uvicorn on port 8001).

### Notable Design Choices
- Agents produce structured function responses; the backend keeps the transport thin.
- Clear separation of platform models vs UI models to decouple API shape from UI needs.
- Strong logging across layers; no silent error suppression.


