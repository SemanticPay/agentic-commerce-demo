from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import uuid
from datetime import datetime
import logging
import sys
import time

from agent.backend.agents.orchestrator.agent import call_agent
from agent.backend.types.types import AgentCallRequest, FunctionPayload, QueryRequest, QueryResponse, AddToCartRequest, \
    AddToCartResponse

session_id_to_cart = {}

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables")
load_dotenv()
logger.info("Environment variables loaded")

logger.info("Initializing FastAPI application")
app = FastAPI(
    title="Shopping Agent API",
    description="HTTP API for the AI Shopping Assistant Agent",
    version="1.0.0",
)
logger.info("FastAPI application initialized")

# Add CORS middleware
logger.info("Adding CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware added successfully")


# @app.post("/add-to-cart", response_model=FunctionPayload, status_code=200)
# async def add_to_cart(request: AddToCartRequest):
#     """Add an item to the cart"""
#     logger.info(f"Adding item {request.item_id} to cart")
#     session_id = request.session_id or str(uuid.uuid4())
#     logger.info(f"Session ID: {session_id}")

#     if not session_id in session_id_to_cart.keys():
#         session_id_to_cart[session_id] = {request.item_id: request.quantity}
#     elif request.item_id not in session_id_to_cart[session_id].keys():
#         session_id_to_cart[session_id][request.item_id] = request.quantity
#     else:
#         session_id_to_cart[session_id][request.item_id] = session_id_to_cart[session_id][request.item_id] + request.quantity

#     logger.info("Building add to cart response")
#     response = AddToCartResponse(
#         status="success",
#         session_id=session_id
#     )
#     logger.info("adding to cart completed successfully")
#     logger.info("=" * 60)
#     return response


# @app.post("/remove-from-cart", response_model=FunctionPayload, status_code=200)
# async def remove_from_cart(request: AddToCartRequest):
#     """Add an item to the cart"""
#     logger.info(f"Adding item {request.item_id} to cart")
#     session_id = request.session_id or str(uuid.uuid4())
#     logger.info(f"Session ID: {session_id}")

#     if session_id in session_id_to_cart.keys():
#         session_id_to_cart[session_id].pop(request.item_id)

#     logger.info("Building remove from cart response")
#     response = AddToCartResponse(
#         status="success",
#         session_id=session_id
#     )
#     logger.info("removing from completed successfully")
#     logger.info("=" * 60)
#     return response


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Send a query to the shopping agent and get a response.

    Args:
        request: QueryRequest containing the user's question, optional session_id, and chat_history

    Returns:
        QueryResponse with the agent's answer and updated chat history and products details
    """
    logger.info("="*60)
    logger.info("Query endpoint called")
    logger.info(f"Question: {request.question}")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"Session ID: {session_id}")

        logger.info("Calling agent with question, context, and products data")
        while True:
            logger.info("Invoking call_agent function")
            agent_resp = await call_agent(
                req=AgentCallRequest(
                    question=request.question,
                    session_id=session_id,
                ),
            )

            if not agent_resp.answer and not agent_resp.function_payloads:
                logger.warning("Agent returned no answer and no function payloads, retrying...")
                time.sleep(1)  # Brief pause before retrying
            else:
                logger.info("Agent returned a valid response")
                break

        logger.info("Agent response received")
        logger.info(f"Agent answer: {agent_resp.answer if agent_resp else 'No response'}")
        logger.info(f"Function payloads count: {len(agent_resp.function_payloads) if agent_resp.function_payloads else 0}")

        logger.info("Creating widgets from function payloads")
        widgets = extract_widgets_from_function_payloads(agent_resp.function_payloads) if agent_resp else []
        logger.info(f"Created {len(widgets)} widget(s)")

        # Update session with new messages
        current_time = datetime.now().isoformat()
        logger.info(f"Updating session at {current_time}")

        logger.info("Building query response")
        response = QueryResponse(
            response=agent_resp.answer if agent_resp else "No response generated",
            status="success",
            session_id=session_id,
            widgets=widgets,
        )
        logger.info("Query completed successfully")
        logger.info("="*60)
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


def extract_widgets_from_function_payloads(function_payloads: list[FunctionPayload]):
    """Extract widgets from function payloads
    
    NOTE: This function is tied to the specific function names used in the agent tools.
    """
    widgets: list[Any] = []
    logger.info(f"Extracting widgets from {len(function_payloads)} function payloads")
    for payload in function_payloads:
        logger.info(f"Processing payload: {payload.name} --> {payload.payload}")
        if payload.name == "create_products_widgets":
            logger.info(f"Adding product widgets from payload: {payload.name} -- {len(payload.payload) if payload.payload else 0} items")
            widgets.extend(payload.payload) # type: ignore
        elif payload.name == "create_cart_widget":
            logger.info(f"Adding cart widget from payload: {payload.name}")
            widgets.append(payload.payload)
        elif payload.name == "create_products_section_widget":
            logger.info(f"Adding product section widget from payload: {payload.name}")
            widgets.append(payload.payload)
    logger.info(f"Widget extraction completed -- {len(widgets)} widget(s) extracted -- {widgets}")
    return widgets


if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Starting Shopping Agent API Server")
    logger.info("="*60)
    logger.info("Running server on http://0.0.0.0:8001")
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
