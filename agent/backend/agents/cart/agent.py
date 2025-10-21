import logging
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent

from agent.backend.tools.cart.tools import  cart_create, cart_get
from agent.backend.tools.interface.tools import  create_cart_widget
from agent.backend.agents.cart.prompt import PROMPT


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

logger.info("Creating cart-agent")
cart_agent = Agent(
            model="gemini-2.5-flash",
            name="cart_agent",
            description="A shopping cart management agent",
            instruction=PROMPT,
            tools=[
                cart_create,
                cart_get,
                create_cart_widget,
            ]
        )
logger.info("cart-agent created successfully")
