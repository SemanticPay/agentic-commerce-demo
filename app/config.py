from pydantic import BaseModel
import os


class AgentConfig(BaseModel):
    mcp_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")


config = AgentConfig()