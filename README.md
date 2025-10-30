# Agentic Commerce MCP Demo

An AI-powered shopping assistant demonstrating multi-agent orchestration (Google ADK) integrated with Shopify. The backend returns structured widgets that the frontend renders into a modern shopping experience.

## Overview

- Multi-agent orchestration with clear division of responsibilities: context gathering, product discovery, cart, and product details.
- Shopify Storefront/Admin GraphQL integration via typed clients.
- FastAPI backend exposes a single `POST /query` endpoint returning widgets ready for UI rendering.
- React (Vite) frontend-v2 provides chat, catalog, product, and cart experiences.

## Features

- Orchestrator agent coordinating sub-agents with dedicated prompts
- Search and product detail retrieval from Shopify
- In-memory cart management and cart creation via Shopify `cartCreate`
- Widget-based UI contract: PRODUCT, PRODUCT_SECTIONS, CART
- Strong logging and explicit error propagation (no silent fallbacks)

## Architecture (High-Level)

- FastAPI service → calls Orchestrator Agent (Google ADK) → delegates to sub-agents → tools read/write state and call Shopify → backend serializes tool outputs into `widgets`.
- Clear separation between platform models (`agent/backend/client/base_types.py`) and UI models (`agent/backend/types/types.py`).

See `docs/BACKEND_ARCHITECTURE.md` and `docs/PROJECT_OVERVIEW.md` for details.

## Prerequisites

- Python 3.12+
- Node.js 18+
- Shopify Storefront/Admin access (endpoints/tokens)

## Setup

1) Python environment and dependencies

```bash
# If a venv already exists in ./venv, activate it; otherwise create it
test -d venv && source venv/bin/activate || (python3 -m venv venv && source venv/bin/activate)
pip install -r requirements.txt
```

2) Frontend dependencies (v2)

```bash
cd agent/frontend-v2
npm install
```

3) Configuration

```bash
cp .env.example .env
```
Set the following environment variables as applicable:
- `SHOPIFY_STOREFRONT_STORE_URL`
- `SHOPIFY_STOREFRONT_ACCESS_TOKEN` (if required by your store)
- `SHOPIFY_ADMIN_API_STORE_URL`
- `SHOPIFY_ADMIN_API_ACCESS_TOKEN`

## Running

1) Backend (FastAPI on :8001)

```bash
make agent-backend
```

2) Frontend (Vite dev server)

```bash
make agent-frontend
```

## API Reference

### POST /query

Request
```json
{
  "question": "I'm looking for a blue bag",
  "session_id": "optional-stable-id"
}
```

Response
```json
{
  "response": "Here are some options!",
  "status": "success",
  "session_id": "uuid-or-provided",
  "widgets": [
    {
      "type": "PRODUCT_SECTIONS",
      "data": { "sections": [/* ... */] },
      "raw_html_string": "<h2>...</h2>..."
    },
    { "type": "PRODUCT", "data": { "id": "...", "title": "..." }, "raw_html_string": "..." },
    { "type": "CART", "data": { "checkout_url": "..." }, "raw_html_string": "..." }
  ]
}
```

Notes
- `session_id` should be reused for continuity; if omitted, the backend generates one.
- Widgets map directly to tool outputs; render either by using `raw_html_string` or by mapping `data` to components.

## Development

- Logging: Extensive INFO-level logs across agents, tools, and clients.
- Error handling: HTTP/GraphQL and runtime errors are raised and surfaced; no default/fallback values are injected.
- Agents: Prompts in `agent/backend/agents/*/prompt.py`; composition in `agents/orchestrator/agent.py`.
- Tools: Implemented in `agent/backend/tools/*` and operate over a shared ToolContext state (keys in `state/keys.py`).

## Project Structure (Essentials)

```
agent/backend/
  main.py                  # FastAPI app and /query endpoint
  agents/                  # orchestrator + sub-agents (context, discovery, cart, product_details)
  tools/                   # context/product/interface/cart tools
  client/                  # Shopify clients (Storefront/Admin) + base types + factory
  types/                   # UI-facing API/types for widgets and responses
  state/keys.py            # ToolContext state keys
agent/frontend-v2/
  src/App.tsx              # Router (/, /chat, /catalog, /cart, /product/:id)
  src/components/*         # Pages and UI components
docs/
  BACKEND_ARCHITECTURE.md  # Detailed backend architecture
  PROJECT_OVERVIEW.md      # End-to-end overview
```

## Documentation

- Backend architecture: `docs/BACKEND_ARCHITECTURE.md`
- Project overview: `docs/PROJECT_OVERVIEW.md`

## Troubleshooting

- 401/403 from Shopify: verify tokens and store URLs in `.env`.
- Empty `widgets`: ensure agents/tools are enabled and that queries match product data; check server logs.
- Timeouts: inspect network connectivity to Shopify GraphQL endpoints; adjust timeouts if needed.

