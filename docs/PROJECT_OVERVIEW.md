## Agentic Commerce MCP Demo — Project Overview

This document summarizes the architecture, flows, and key modules of the project. It is concise by design while remaining complete enough for onboarding and maintenance.

### High-Level Architecture
- **Backend (`agent/backend/`)**: FastAPI service exposing a single chat endpoint that orchestrates a hierarchy of AI agents (built on Google ADK) and platform tools (Shopify storefront/admin). Produces structured UI widgets for the frontend to render.
- **Frontend (`agent/frontend-v2/`)**: React + Vite app with routes for chat, catalog, product, and cart. Renders widgets returned by the backend (work-in-progress wiring) and offers a modern UX.
- **Integration**: Agents call tools that query Shopify and assemble widgets. Backend translates agent function payloads into a `widgets` array in the `QueryResponse`.

### Backend

#### Entry Point and API
- `agent/backend/main.py`
  - FastAPI app with CORS; main endpoint: `POST /query`.
  - Request: `QueryRequest { question: str, session_id?: str }`.
  - Response: `QueryResponse { response: str, status: "success", session_id, widgets: Any[] }`.
  - Calls `agents.orchestrator.agent.call_agent(...)`, then converts function payloads to `widgets` via `extract_widgets_from_function_payloads`.

#### Types and State
- `types/types.py`: UI-level models for product, cart, widgets, and API contracts.
- `state/keys.py`: Well-known keys for agent tool state: `X-cart`, `X-search-categories`, `X-shopify-cart`, `X-product-sections`.

#### Orchestrator and Sub-Agents
- `agents/orchestrator/agent.py`
  - Orchestrator `Agent` with model `gemini-2.0-flash-lite`, instruction in `agents/orchestrator/prompt.py`.
  - Sub-agents: `context_agent`, `discovery_agent`, `cart_agent`, `product_details_agent`.
  - Uses `google.adk` services: `Runner`, `InMemorySessionService`, `InMemoryArtifactService`.
  - `call_agent` maintains a per-user session and streams events to collect text and function payloads.
- Sub-agent prompts:
  - `context`: clarify needs and write search categories to state.
  - `discovery`: search for products and create product section widgets.
  - `cart`: manage in-memory cart and, on request, create a Shopify cart + cart widget.
  - `product_details`: fetch and summarize a single product by ID.

#### Tools (MCP functions)
- `tools/context/tools.py`
  - `set_search_categories(raw_categories, tool_context)` → write `SearchCategory[]` to `X-search-categories`.
  - `get_search_categories(tool_context)` → read categories.
- `tools/product/tools.py`
  - Initializes a `StoreFrontClient` via `client.factory.get_storefront_client(StoreProvider.SHOPIFY, store_url=env)`.
  - `search_product_categories(tool_context)`: uses categories from state, queries products, and writes `ProductSection[]` to `X-product-sections`.
  - `search_products(query)` → flattens Shopify products/variants → returns UI `ProductList`.
  - `get_product_details(product_id)` → returns a single UI `Product` (first variant).
- `tools/interface/tools.py`
  - `create_products_widgets(raw_prod_list)` → `ProductWidget[]` with HTML snippets and data.
  - `create_products_section_widget(tool_context)` → `Widget` of type `PRODUCT_SECTIONS` using `X-product-sections`.
  - `create_cart_widget(tool_context)` → `Widget` of type `CART` from `X-shopify-cart`.
- `tools/cart/tools.py`
  - In-memory cart ops: `add_item_to_cart`, `remove_item_from_cart` stored in `X-cart`.
  - `create_shopify_cart_and_get_checkout_url` builds lines from `X-cart`, calls Shopify `cartCreate`, stores a summarized `Cart` in `X-shopify-cart`.

#### Shopify Clients
- `client/base_types.py`: Strongly-typed request/response models to normalize Shopify responses.
- `client/factory.py`: Provider switch, currently supports `SHOPIFY` → `ShopifyGraphQLClient` (Storefront) and `ShopifyAdminClient` (Admin).
- `client/shopify.py`:
  - `ShopifyGraphQLClient` (Storefront): `search_products`, `cart_create`, `cart_get`, `get_product` using GraphQL.
  - `ShopifyAdminClient` (Admin): `get_products` with pagination.
  - Extensive logging; raises on HTTP/GraphQL errors (no silent fallbacks).

#### Data Flow (one turn)
1) Frontend calls `POST /query` with `question` (+ optional `session_id`).
2) Backend generates/propagates `session_id`, invokes `call_agent`.
3) Orchestrator delegates to sub-agents; tools read/write state and return function responses.
4) Backend extracts function payloads and emits `widgets` aligned with known tool names.
5) Frontend renders widgets (data + optional HTML string).

### Frontend (v2)
- Location: `agent/frontend-v2` (preferred app).
- Router: `HashRouter` with routes: `/` (Home), `/chat`, `/catalog`, `/cart`, `/product/:id`.
- Pages:
  - `HomePage`: search entry; navigates to `/chat` (TODO: wire to backend).
  - `ChatPage`: collects user input; intended to call backend and then navigate to `/catalog` when widgets available.
  - `CatalogPage`: displays categorized product grids; expects catalog/widgets from backend (TODO wiring).
  - `CartPage`: shows editable cart and summary; intended to hook to cart widgets/checkout URL.
- UI kit: `components/ui/*` (buttons, inputs, dialogs, etc.) and `figma/ImageWithFallback`.

### API Contract (Backend ↔ Frontend)
- `POST /query`
  - Request: `{ question: string, session_id?: string }`
  - Response:
    - `response`: brief natural-language text from agent.
    - `status`: "success" | error via 500 HTTPException.
    - `session_id`: stable per user; reuse in subsequent calls.
    - `widgets`: list of objects originating from tool names:
      - From `create_products_widgets`: multiple `PRODUCT` widgets `{ type, data: { id,title,description,price,currency,image }, raw_html_string }`.
      - From `create_products_section_widget`: one `PRODUCT_SECTIONS` widget `{ type, data: { sections }, raw_html_string }`.
      - From `create_cart_widget`: one `CART` widget `{ type, data: { checkout_url, totals... }, raw_html_string }`.

### Configuration & Running
- Requirements: Python 3.12+, Node 18+.
- Environment: `.env` with Shopify endpoints/tokens:
  - `SHOPIFY_STOREFRONT_STORE_URL` (GraphQL endpoint)
  - `SHOPIFY_STOREFRONT_ACCESS_TOKEN` (optional, if required)
  - `SHOPIFY_ADMIN_API_STORE_URL`, `SHOPIFY_ADMIN_API_ACCESS_TOKEN` for Admin client tests
- Install and run:
  - Backend: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && make agent-backend`
  - Frontend (v2): `cd agent/frontend-v2 && npm install && npm run dev`

### Notable Design Choices
- Clear separation between platform client types (`client/base_types.py`) and UI-facing types (`types/types.py`).
- Agent-first orchestration with explicit, inspectable tool invocations; backend only transforms function payloads to widgets.
- No hidden defaults or silent fallbacks; errors are logged and raised.

### TODOs / Open Wiring
- Frontend pages have TODOs to call `POST /query` and render `widgets` (translate to components or use `raw_html_string`).
- Discovery agent currently registers only selected tools; enable/adjust as needed.
- Expand widget rendering coverage and typing on the frontend.

### Repository Map (essentials)
- Backend: `agent/backend/{main.py, agents/*, tools/*, client/*, types/*, state/*}`
- Frontend v2: `agent/frontend-v2/src/{App.tsx, components/*, ui/*}`
- Root docs: `README.md` (quick start), `docs/PROJECT_OVERVIEW.md` (this doc)

