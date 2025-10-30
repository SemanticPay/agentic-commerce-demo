import logging
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent

from agent.backend.agents.product_details.prompt import PROMPT
from agent.backend.tools.product.tools import get_product_details


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

logger.info("Creating product_details-agent")
product_details_agent = Agent(
            model="gemini-2.5-flash",
            name="product_details_agent",
            description="A product_details information retrieval agent",
            instruction=PROMPT,
            tools=[
                get_product_details,
            ]
        )
logger.info("product_details-agent created successfully")
