from google.adk.agents.llm_agent import LlmAgent
from app.subagents.cart.agent import cart_agent
from app.subagents.product.agent import product_agent
from .prompt import instruction


root_agent = LlmAgent(
    name="shopper_agent",
    model="gemini-2.5-flash",
    instruction=instruction,
    sub_agents=[cart_agent,product_agent],
)