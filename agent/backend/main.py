from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import uuid
from datetime import datetime

try:
    from .agent import call_agent
    from .widgets import CartWidget, ProductWidget, Widget, WidgetType
    from .base_types import FunctionPayload, QueryRequest, QueryResponse, ChatMessage, AgentCallRequest
except ImportError:
    from agent import call_agent
    from widgets import CartWidget, ProductWidget, Widget, WidgetType
    from base_types import FunctionPayload, QueryRequest, QueryResponse, ChatMessage, AgentCallRequest

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Shopping Agent API",
    description="HTTP API for the AI Shopping Assistant Agent",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# In-memory session storage (in production, use a proper database)
sessions: Dict[str, List[ChatMessage]] = {}


@app.get("/")
async def root():
    """Root endpoint with API information"""
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
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Get existing chat history or use provided history
        if session_id in sessions:
            chat_history = sessions[session_id]
        else:
            chat_history = request.chat_history or []
            sessions[session_id] = []

        # Convert chat_history to dict format if it's from Pydantic models
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

        # Call the agent with full context
        agent_resp = await call_agent(
            req=AgentCallRequest(
                question=request.question,
                chat_history=history_dicts,
                session_id=session_id,
            ),
        )

        widgets = create_widgets_from_function_payload(agent_resp.function_payloads)

        # Update session with new messages
        current_time = datetime.now().isoformat()

        # Add user message
        user_message = ChatMessage(
            role="user", content=request.question, timestamp=current_time
        )
        sessions[session_id].append(user_message)

        # Add agent response
        agent_message = ChatMessage(
            role="agent",
            content=agent_resp.answer if agent_resp else "No response generated",
            timestamp=current_time,
        )
        sessions[session_id].append(agent_message)

        return QueryResponse(
            question=request.question,
            response=agent_resp.answer if agent_resp else "No response generated",
            status="success",
            session_id=session_id,
            updated_chat_history=sessions[session_id],
            widgets=widgets,
        )
    except Exception as e:
        print("Error processing query:", str(e))
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
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return {"session_id": session_id, "chat_history": sessions[session_id]}


def create_widgets_from_function_payload(func_payloads: list[FunctionPayload]) -> List[Widget]:
    ws: List[Widget] = []

    for func_payload in func_payloads:
        if not func_payload or not func_payload.payload:
            return ws

        if func_payload.name == "search_products":
            products = func_payload.payload.get("products", [])
            for prod in products:
                if prod:
                    ws.append(create_product_widget(prod))
        elif func_payload.name in ["cart_get", "cart_create"]:
            cart = func_payload.payload.get("cart", {})
            if cart:
                ws.append(create_cart_widget(cart))

    return ws


def create_product_widget(prod: dict) -> Widget:
    # ui_resource = create_ui_resource({
    #     "uri": "ui://product-card-demo",
    #     "content": {
    #         "type": "rawHtml",
    #         "htmlString": f"""
    #         <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; max-width: 300px; font-family: Arial, sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    #             <img src="{item.get('image_url')}" 
    #                  style="width: 100%; height: 200px; object-fit: cover; border-radius: 4px; margin-bottom: 12px;" 
    #                  alt="{item.get('title')}"/>
    #             <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #333;">{item.get('title')}</h3>
    #             <p style="margin: 0; font-size: 20px; font-weight: bold; color: #007bff;">{item.get('price')}</p>
    #         </div>
    #         """
    #     },
    #     "encoding": "text"
    # })
    ui_resource = f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; max-width: 300px; font-family: Arial, sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <img src="{prod.get('image_url')}" 
                    style="width: 100%; height: 200px; object-fit: cover; border-radius: 4px; margin-bottom: 12px;" 
                    alt="{prod.get('title')}"/>
            <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #333;">{prod.get('title')}</h3>
            <p style="margin: 0; font-size: 20px; font-weight: bold; color: #007bff;">{prod.get('price')}</p>
        </div>
    """

    return ProductWidget(
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


def create_cart_widget(cart: dict) -> Widget:
    # ui_resource = create_ui_resource({
    #     "uri": "ui://product-card-demo",
    #     "content": {
    #         "type": "rawHtml",
    #         "htmlString": f"""
    #         <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; max-width: 300px; font-family: Arial, sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    #             <img src="{item.get('image_url')}" 
    #                  style="width: 100%; height: 200px; object-fit: cover; border-radius: 4px; margin-bottom: 12px;" 
    #                  alt="{item.get('title')}"/>
    #             <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #333;">{item.get('title')}</h3>
    #             <p style="margin: 0; font-size: 20px; font-weight: bold; color: #007bff;">{item.get('price')}</p>
    #         </div>
    #         """
    #     },
    #     "encoding": "text"
    # })
    ui_resource = f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; max-width: 300px; font-family: Arial, sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <img src="{prod.get('image_url')}" 
                    style="width: 100%; height: 200px; object-fit: cover; border-radius: 4px; margin-bottom: 12px;" 
                    alt="{prod.get('title')}"/>
            <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #333;">{prod.get('title')}</h3>
            <p style="margin: 0; font-size: 20px; font-weight: bold; color: #007bff;">{prod.get('price')}</p>
        </div>
    """

    return CartWidget(
        type=WidgetType.CART,
        data={
            "checkout_url": cart.get("checkout_url"),
            "subtotal_amount": cart.get("subtotal_amount", {}).get("amount"),
            "subtotal_amount_currency_code": cart.get("subtotal_amount", {}).get("currency_code"),
            "tax_amount": cart.get("tax_amount", {}).get("amount"),
            "tax_amount_currency_code": cart.get("tax_amount", {}).get("currency_code"),
            "total_amount": cart.get("total_amount", {}).get("amount"),
            "total_amount_currency_code": cart.get("total_amount", {}).get("currency_code"),
        },
    )

if __name__ == "__main__":
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
