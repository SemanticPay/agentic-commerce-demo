from typing import Any, Optional, List
from pydantic import BaseModel, Field


class FunctionPayload(BaseModel):
    name: str
    payload: Any | None = None


class AgentCallRequest(BaseModel):
    question: str
    session_id: str | None = None


class AgentCallResponse(BaseModel):
    answer: str
    function_payloads: list[FunctionPayload] = Field(default_factory=list)


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "question": "I am looking for a bag",
                "session_id": "session_123",
            }
        }


class QueryResponse(BaseModel):
    response: str
    status: str
    session_id: Optional[str] = None
    widgets: list[Any] = Field(default_factory=list)
