import logging
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from agent.backend.tools.product.tools import search_products
from agent.backend.tools.interface.tools import create_products_widgets
from .prompt import RETRIEVAL_FORMAT_PROMPT, WIDGETS_PROMPT, SANITIZER_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

load_dotenv()

retrieval_and_format_agent = Agent(
    model="gemini-2.0-flash",
    name="retrieval_and_format_agent",
    description="Fetches product data and outputs structured JSON for rendering.",
    instruction=RETRIEVAL_FORMAT_PROMPT,
    tools=[search_products],
)

render_agent = Agent(
    model="gemini-2.5-flash",
    name="render_agent",
    description="Renders structured products into visual UI widgets.",
    instruction=WIDGETS_PROMPT,
    tools=[create_products_widgets],
)

sanitizer_agent = Agent(
    model="gemini-2.0-flash",
    name="sanitizer_agent",
    description="Cleans and humanizes final output by removing structured text.",
    instruction=SANITIZER_PROMPT,
)

discovery_agent = SequentialAgent(
    name="discovery_agent",
    description="Simplified deterministic discovery pipeline: retrieval+formatting → rendering → sanitization",
    sub_agents=[
        retrieval_and_format_agent,
        render_agent,
        sanitizer_agent,
    ],
)