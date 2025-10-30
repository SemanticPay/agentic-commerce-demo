import logging
import sys
from typing import Any

from google.adk.tools import ToolContext

from agent.backend.state import keys
from agent.backend.types.types import SearchCategory


# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def set_search_categories(raw_categories: list[dict[str, Any]], tool_context: ToolContext) -> None:
    cats = []
    for raw_cat in raw_categories:
        cat = SearchCategory(
            title=raw_cat.get("title", ""),
            subtitle=raw_cat.get("subtitle", ""),
            description=raw_cat.get("description", ""),
            query=raw_cat.get("query", ""),
        )
        logger.info(f"Parsed search category: \nraw -> {raw_cat}\nparsed -> {cat}")
        cats.append(cat)

    logger.info(f"Setting search categories in state: {cats}")
    tool_context.state[keys.SEARCH_CATEGORIES_STATE_KEY] = cats


def get_search_categories(tool_context: ToolContext) -> list[SearchCategory]:
    categories = tool_context.state.get(keys.SEARCH_CATEGORIES_STATE_KEY, [])
    logger.info(f"Retrieved categories from state: {categories}")
    return categories
