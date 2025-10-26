import logging
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent

from agent.backend.tools.product.tools import search_products, get_product_details
from agent.backend.tools.interface.tools import create_products_widgets
from agent.backend.agents.product.prompt import PROMPT


# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
logger.info("Loading environment variables for agent")
load_dotenv()
logger.info("Environment variables loaded")

logger.info("Creating product-agent")
product_agent = Agent(
            model="gemini-2.5-flash",
            name="product_agent",
            description="A product information retrieval agent",
            instruction=PROMPT,
            tools=[
                search_products,
                get_product_details,
                create_products_widgets,
            ]
        )
logger.info("product-agent created successfully")
