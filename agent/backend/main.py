from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import uuid
from datetime import datetime
from mcp_ui_server import create_ui_resource

from agent import async_main

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


class ChatMessage(BaseModel):
    role: str  # "user" or "agent"
    content: str
    timestamp: Optional[str] = None


# In-memory session storage (in production, use a proper database)
sessions: Dict[str, List[ChatMessage]] = {}


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Find me a machine learning course",
                "session_id": "session_123",
                "chat_history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "agent", "content": "Hi! How can I help you today?"},
                ],
            }
        }


class QueryResponse(BaseModel):
    question: str
    response: str
    status: str
    session_id: Optional[str] = None
    updated_chat_history: Optional[List[ChatMessage]] = []
    ui_objects: list[Any] = Field(default_factory=list)


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
        response, items = await async_main(
            question=request.question, chat_history=history_dicts, session_id=session_id
        )
        ui_resources = []

        # https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRSCTJxNM1ZuXKk4EGRpGh5FAP-4Rlf8rmcdA&s
        for item in items:
            ui_resource = create_ui_resource({
                "uri": "ui://product-card-demo",
                "content": {
                    "type": "rawHtml",
                    "htmlString": f"""
                    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; max-width: 300px; font-family: Arial, sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <img src="{item.get('image_url')}" 
                             style="width: 100%; height: 200px; object-fit: cover; border-radius: 4px; margin-bottom: 12px;" 
                             alt="{item.get('title')}"/>
                        <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #333;">{item.get('title')}</h3>
                        <p style="margin: 0; font-size: 20px; font-weight: bold; color: #007bff;">{item.get('price')}</p>
                    </div>
                    """
                },
                "encoding": "text"
            })
            ui_resources.append(ui_resource)

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
            content=response if response else "No response generated",
            timestamp=current_time,
        )
        sessions[session_id].append(agent_message)


        return QueryResponse(
            question=request.question,
            response=response if response else "No response generated",
            status="success",
            session_id=session_id,
            updated_chat_history=sessions[session_id],
            ui_objects=ui_resources,
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


if __name__ == "__main__":
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
