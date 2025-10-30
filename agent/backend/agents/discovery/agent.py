import logging
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent

from agent.backend.tools.product.tools import search_products
from agent.backend.tools.interface.tools import create_products_widgets
from agent.backend.agents.discovery.prompt import PROMPT


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("Loading environment variables for agent")
load_dotenv()
logger.info("Environment variables loaded")

logger.info("Creating discovery-agent")
discovery_agent = Agent(
            model="gemini-2.0-flash-lite",
            name="discovery_agent",
            description="A discovery information retrieval agent",
            instruction=PROMPT,
            tools=[
                search_products,
                create_products_widgets,
            ]
        )
logger.info("discovery-agent created successfully")
