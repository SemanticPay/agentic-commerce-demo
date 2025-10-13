from typing import Any, Optional, List
from pydantic import BaseModel, Field


class FunctionPayload(BaseModel):
    name: str
    payload: Any | None = None


class AgentCallRequest(BaseModel):
    question: str
    chat_history: list[dict] = []
    session_id: str | None = None


class AgentCallResponse(BaseModel):
    answer: str
    function_payloads: list[FunctionPayload] = Field(default_factory=list)


class ChatMessage(BaseModel):
    role: str  # "user" or "agent"
    content: str
    timestamp: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "question": "I am looking for a bag",
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
    widgets: list[Any] = Field(default_factory=list)
