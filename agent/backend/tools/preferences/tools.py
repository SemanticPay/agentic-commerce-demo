import logging
import sys

from google.adk.tools import ToolContext

from agent.backend.tools.preferences.backend.tools import InMemoryPreferencesBackend
from agent.backend.types.types import UserPreferences
from agent.backend.tools.preferences.backend.types import UserPreferences as InternalUserPreferences


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


BACKEND = InMemoryPreferencesBackend()


def get_user_preferences(user_id: str, tool_context: ToolContext) -> UserPreferences | None:
    pref = BACKEND.get_user_preferences(user_id) 
    if not pref:
        return None

    return UserPreferences(
        preferred_currency=pref.preferred_currency,
        favorite_categories=pref.favorite_categories,
        price_range=pref.price_range
    )


def set_user_preferences(user_id: str, pref: UserPreferences) -> None:
    internal_pref = InternalUserPreferences(
        preferred_currency=pref.preferred_currency,
        favorite_categories=pref.favorite_categories,
        price_range=pref.price_range
    )
    BACKEND.set_user_preferences(user_id, internal_pref) 

    