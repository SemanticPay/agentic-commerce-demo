from abc import ABC, abstractmethod
import logging
import sys

from agent.backend.tools.preferences.backend.types import UserPreferences


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class PreferenceBackend(ABC):
    """Interface for user preferences backend."""

    @abstractmethod
    def get_user_preferences(self, user_id: str) -> UserPreferences | None:
        pass

    @abstractmethod
    def set_user_preferences(self, user_id: str, pref: UserPreferences) -> None:
        pass


class InMemoryPreferencesBackend(PreferenceBackend):
    """Backend for managing user preferences."""
    def __init__(self):
        self.user_preferences = {}

    def get_user_preferences(self, user_id: str) -> UserPreferences | None:
        return self.user_preferences.get(user_id)

    def set_user_preferences(self, user_id: str, pref: UserPreferences) -> None:
        self.user_preferences[user_id] = pref
