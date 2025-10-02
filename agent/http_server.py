import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from agent import async_main

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Shopping Agent API",
    description="HTTP API for the AI Shopping Assistant Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Find me a machine learning course"
            }
        }


class QueryResponse(BaseModel):
    question: str
    response: str
    status: str


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Shopping Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /query": "Send a question to the shopping agent",
            "GET /health": "Health check endpoint"
        }
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
        request: QueryRequest containing the user's question
        
    Returns:
        QueryResponse with the agent's answer
    """
    try:
        # Capture the agent's response
        # We need to modify async_main to return the response instead of just printing
        response = await async_main(request.question)
        
        return QueryResponse(
            question=request.question,
            response=response if response else "No response generated",
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "http_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
