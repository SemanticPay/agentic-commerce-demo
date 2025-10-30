import logging
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent

from agent.backend.agents.context.prompt import PROMPT
from agent.backend.tools.context.tools import set_search_categories


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

logger.info("Creating context-agent")
context_agent = Agent(
            model="gemini-2.0-flash-lite",
            name="context_agent",
            description="A shopping context agent",
            instruction=PROMPT,
            tools=[
                set_search_categories,
            ],
        )
logger.info("context-agent created successfully")
