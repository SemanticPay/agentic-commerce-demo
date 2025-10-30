import logging
import sys
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from agent.backend.tools.product.tools import search_products
from agent.backend.tools.interface.tools import create_products_widgets
from .prompt import RETRIEVAL_PROMPT, WIDGETS_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

load_dotenv()

discovery_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="discovery_agent",
    description="End-to-end fashion discovery agent combining product search and widget rendering.",
    instruction=(
        """
You are the Discovery AI for a shopping assistant.

**Goal**
Help users find fashion items (bags, shoes, clothes, accessories), render them as UI widgets, and give a short, friendly message.

**Tools**
- search_products(query: str): Search the store catalog.
- create_products_widgets(raw_prod_list: list[dict]): Create UI widgets for the discovered products.

**Task Flow**
1. Always start by calling search_products using the user's request as the query.
2. Pass the products returned to create_products_widgets to display them visually.
3. Then, reply to the user with a short, human message describing what was found.

**Rules**
- Never show raw JSON, HTML, or tool output.
- Never mention tools or internal logic.
- Keep your message warm, casual, and concise.
- If no products are found, politely say so and suggest refining the search.
- Example of valid final message: “Here are some options you might like!”

Respond only with the final friendly message.
"""
    ),
    tools=[search_products, create_products_widgets],
)
