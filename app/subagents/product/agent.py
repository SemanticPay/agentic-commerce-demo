from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from app.config import config
from .prompt import instruction

_product_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=config.mcp_url)
)

product_agent = LlmAgent(
    name="product_agent",
    model="gemini-2.5-flash",
    instruction=instruction,
    tools=[_product_toolset],
)