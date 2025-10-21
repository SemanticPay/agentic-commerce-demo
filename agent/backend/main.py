from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import uuid
from datetime import datetime
import logging
import sys
import time

from agent.backend.agents.root.agent import call_agent
from agent.backend.types.types import AgentCallRequest, QueryRequest, QueryResponse

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


def extract_widgets_from_function_payloads(function_payloads):
    """Extract widgets from function payloads"""
    widgets = []
    logger.info(f"Extracting widgets from {len(function_payloads)} function payloads")
    for payload in function_payloads:
        logger.info(f"Processing payload: {payload.name} --> {payload.payload}")
        if payload.name == "create_products_widgets":
            logger.info(f"Adding widget from payload: {payload.name}")
            widgets.extend(payload.payload)
        elif payload.name == "create_cart_widget":
            logger.info(f"Adding widget from payload: {payload.name}")
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
