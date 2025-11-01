import logging
import sys

from google.adk.sessions.state import State

from agent.backend.state import keys
from agent.backend.types.types import SearchCategory


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def get_search_query(state: State) -> str:
    query = state.get(keys.SEARCH_QUERY_STATE_KEY, [])
    logger.info(f"Retrieved query from state: {query}")
    return query

def get_search_categories(state: State) -> list[SearchCategory]:
    categories = state.get(keys.SEARCH_CATEGORIES_STATE_KEY, [])
    logger.info(f"Retrieved categories from state: {categories}")
    return categories
