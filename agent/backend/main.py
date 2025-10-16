from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import uuid
from datetime import datetime
import logging
import sys
import time

try:
    from .agent import call_agent
    from .widgets import CartWidget, ProductWidget, Widget, WidgetType
    from .base_types import FunctionPayload, QueryRequest, QueryResponse, ChatMessage, AgentCallRequest
except ImportError:
    from agent import call_agent
    from widgets import CartWidget, ProductWidget, Widget, WidgetType
    from base_types import FunctionPayload, QueryRequest, QueryResponse, ChatMessage, AgentCallRequest

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



# In-memory session storage (in production, use a proper database)
sessions: Dict[str, List[ChatMessage]] = {}
logger.info("Session storage initialized")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Shopping Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /query": "Send a question to the shopping agent with full chat context",
            "GET /session/{session_id}": "Get chat history for a specific session",
            "GET /health": "Health check endpoint",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Send a query to the shopping agent and get a response.

    Args:
        request: QueryRequest containing the user's question, optional session_id, and chat_history

    Returns:
        QueryResponse with the agent's answer and updated chat history
    """
    logger.info("="*60)
    logger.info("Query endpoint called")
    logger.info(f"Question: {request.question}")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"Session ID: {session_id}")

        # Get existing chat history or use provided history
        if session_id in sessions:
            logger.info(f"Using existing session with {len(sessions[session_id])} messages")
            chat_history = sessions[session_id]
        else:
            logger.info("Creating new session")
            chat_history = request.chat_history or []
            sessions[session_id] = []
            logger.info(f"Initialized with {len(chat_history)} messages from request")

        # Convert chat_history to dict format if it's from Pydantic models
        logger.info("Converting chat history to dict format")
        history_dicts = []
        for msg in chat_history:
            if isinstance(msg, ChatMessage):
                history_dicts.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                    }
                )
            else:
                history_dicts.append(msg)
        logger.info(f"Converted {len(history_dicts)} messages")

        # Call the agent with full context
        logger.info("Calling agent with question and context")

        while True:
            logger.info("Invoking call_agent function")
            agent_resp = await call_agent(
                req=AgentCallRequest(
                    question=request.question,
                    chat_history=history_dicts,
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
        widgets = create_widgets_from_function_payload(agent_resp.function_payloads)
        logger.info(f"Created {len(widgets)} widget(s)")

        # Update session with new messages
        current_time = datetime.now().isoformat()
        logger.info(f"Updating session at {current_time}")

        # Add user message
        user_message = ChatMessage(
            role="user", content=request.question, timestamp=current_time
        )
        sessions[session_id].append(user_message)
        logger.info("User message added to session")

        # Add agent response
        agent_message = ChatMessage(
            role="agent",
            content=agent_resp.answer if agent_resp else "No response generated",
            timestamp=current_time,
        )
        sessions[session_id].append(agent_message)
        logger.info("Agent message added to session")
        logger.info(f"Session now has {len(sessions[session_id])} total messages")

        logger.info("Building query response")
        response = QueryResponse(
            question=request.question,
            response=agent_resp.answer if agent_resp else "No response generated",
            status="success",
            session_id=session_id,
            updated_chat_history=sessions[session_id],
            widgets=widgets,
        )
        logger.info("Query completed successfully")
        logger.info("="*60)
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """
    Get the chat history for a specific session.

    Args:
        session_id: The session ID to retrieve history for

    Returns:
        Chat history for the session
    """
    logger.info(f"Session history requested for session_id: {session_id}")
    
    if session_id not in sessions:
        logger.warning(f"Session {session_id} not found")
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    logger.info(f"Returning {len(sessions[session_id])} messages for session {session_id}")
    return {"session_id": session_id, "chat_history": sessions[session_id]}


def create_widgets_from_function_payload(func_payloads: list[FunctionPayload]) -> List[Widget]:
    logger.info(f"Creating widgets from {len(func_payloads) if func_payloads else 0} function payloads")
    ws: List[Widget] = []

    for idx, func_payload in enumerate(func_payloads):
        if not func_payload or not func_payload.payload:
            logger.debug(f"Skipping empty payload at index {idx}")
            return ws

        logger.info(f"Processing function payload {idx + 1}: {func_payload.name}")
        
        if func_payload.name == "search_products":
            products = func_payload.payload.get("products", [])
            logger.info(f"Creating product widgets for {len(products)} products")
            for prod_idx, prod in enumerate(products):
                if prod:
                    ws.append(create_product_widget(prod))
                    logger.debug(f"Created product widget {prod_idx + 1}: {prod.get('title', 'Unknown')}")
            logger.info(f"Created {len(products)} product widget(s)")
            
        elif func_payload.name in ["cart_get", "cart_create"]:
            cart = func_payload.payload
            logger.info(f"Creating cart widget for {func_payload.name}")
            if cart:
                ws.append(create_cart_widget(cart))
                logger.info("Cart widget created successfully")

    logger.info(f"Total widgets created: {len(ws)}")
    return ws


def create_product_widget(prod: dict) -> Widget:
    logger.debug(f"Creating product widget for: {prod.get('title', 'Unknown product')}")
    widget = ProductWidget(
        type=WidgetType.PRODUCT,
        data={
            "id": prod.get("id"),
            "title": prod.get("title"),
            "description": prod.get("description"),
            "price": prod.get("price", {}).get("amount"),
            "currency": prod.get("price", {}).get("currency_code"),
            "image_url": prod.get("image_url"),
        },
    )
    logger.debug(f"Product widget created: {prod.get('title')} - {prod.get('price', {}).get('amount')} {prod.get('price', {}).get('currency_code')}")
    return widget


def create_cart_widget(cart: dict) -> Widget:
    logger.debug("Creating cart widget")
    subtotal = cart.get("subtotal_amount", {})
    tax = cart.get("tax_amount", {}) or {}
    total = cart.get("total_amount", {})
    
    logger.debug(f"Cart details - Subtotal: {subtotal.get('amount')} {subtotal.get('currency_code')}, " +
                f"Tax: {tax.get('amount')} {tax.get('currency_code')}, " +
                f"Total: {total.get('amount')} {total.get('currency_code')}")
    
    widget = CartWidget(
        type=WidgetType.CART,
        data={
            "checkout_url": cart.get("checkout_url"),
            "subtotal_amount": subtotal.get("amount"),
            "subtotal_amount_currency_code": subtotal.get("currency_code"),
            "tax_amount": tax.get("amount"),
            "tax_amount_currency_code": tax.get("currency_code"),
            "total_amount": total.get("amount"),
            "total_amount_currency_code": total.get("currency_code"),
        },
    )
    logger.debug("Cart widget created successfully")
    return widget

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Starting Shopping Agent API Server")
    logger.info("="*60)
    logger.info("Running server on http://0.0.0.0:8001")
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
