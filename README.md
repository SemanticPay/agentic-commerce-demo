# Agentic commerce MCP demo

This repository contains a demo of an agentic commerce system implemented via an MCP server using FastMCP. The demo showcases how to leverage AI agents to facilitate and enhance the online shopping experience.

This repo aims to implement the ACP protocol for checkout and payment processing: https://developers.openai.com/commerce/

## Overview

The server has been migrated from a Flask HTTP API to a Model Context Protocol (MCP) server using FastMCP. This allows AI assistants to directly interact with the shopping system through standardized tools.

## Available Tools

The MCP server exposes three main tools:

1. **create_checkout_session**: Create a new checkout session with items and buyer information
2. **search_items**: Search for items by query and keywords
3. **delegate_payment**: Process payment delegation for a checkout session

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Linux/Mac
# or
env\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

To start the MCP server:

```bash
python server.py
```

The server will start and expose the MCP tools for AI assistants to use.

## Integration with AI Assistants

To use this MCP server with an AI assistant like Claude, you'll need to configure it in your MCP settings. The server provides standardized tool interfaces that AI assistants can discover and use automatically.

### MCP Client Configuration

Add the following to your MCP client configuration (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "semanticpay-shopping": {
      "command": "python",
      "args": ["/path/to/mcp-demo/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-demo"
      }
    }
  }
}
```

Replace `/path/to/mcp-demo` with the actual path to this repository.

## Testing

Run the test script to verify all functionality works:

```bash
python test_mcp.py
```

This will test:
- Item search functionality
- Checkout session creation with price calculations
- Payment delegation processing

## Key Changes from HTTP API

The migration from Flask to FastMCP includes:

- **From REST endpoints to MCP tools**: HTTP routes are now MCP tools that can be called by AI assistants
- **Direct type integration**: Uses Pydantic models directly without JSON serialization overhead
- **Tool discovery**: AI assistants can automatically discover available tools and their parameters
- **Standardized protocol**: Uses the Model Context Protocol for consistent AI-to-server communication

## Original Flask Endpoints (Now MCP Tools)

- `POST /api/checkout_sessions` → `create_checkout_session(item_ids, buyer)`
- `GET /api/search` → `search_items(query, keywords)`
- `POST /api/delegate_payment` → `delegate_payment(request)`

## Run chat UI

```
python -m http.server 8080 --directory agent/ui
```
