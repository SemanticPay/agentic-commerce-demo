from abc import ABC, abstractmethod
from client.base_types import SearchProductsResponse


class StoreFrontClient(ABC):
    """
    Abstract interface for storefront clients.
    """
    
    @abstractmethod
    def search_products(
        self,
        query: str = "",
        first: int = 10,
        sort_key: str = "RELEVANCE",
        reverse: bool = False
    ) -> SearchProductsResponse:
        """
        Search for products in the storefront.
        
        Args:
            query: Search query string (e.g., "shoes", "red", "nike")
            first: Number of products to return
            sort_key: Sort key (RELEVANCE, TITLE, PRICE, CREATED_AT, etc.)
            reverse: Whether to reverse the sort order
            
        Returns:
            SearchProductsResponse containing a list of products
        """
        pass

    @abstractmethod
    def create_cart(self):
        pass

    @abstractmethod
    def get_cart(self, cart_id: str):
        pass

    @abstractmethod
    def add_to_cart(self, cart_id: str, product_id: str, quantity: int = 1):
        pass

    @abstractmethod
    def remove_from_cart(self, cart_id: str, product_id: str):
        pass

    @abstractmethod
    def get_payment_url(self, cart_id: str) -> str:
        pass

    @abstractmethod
    def get_payment_status(self, order_id: str) -> str:
        pass
