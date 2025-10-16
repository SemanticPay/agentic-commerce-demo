from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from app.config import config
from .prompt import instruction

_cart_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=config.mcp_url)
)

cart_agent = LlmAgent(
    name="cart_agent",
    model="gemini-2.5-flash",
    instruction=instruction,
    tools=[_cart_toolset],
)