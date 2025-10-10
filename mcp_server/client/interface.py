from abc import ABC, abstractmethod
from base_types import CartCreateResponse, CartCreateRequest, SearchProductsRequest, SearchProductsResponse


class StoreFrontClient(ABC):
    """
    Abstract interface for storefront clients.
    """
    
    @abstractmethod
    def search_products(
        self,
        req: SearchProductsRequest
    ) -> SearchProductsResponse:
        """
        Search for products in the storefront.
        
        Args:
            req (SearchProductsRequest): The search request parameters.
            
        Returns:
            SearchProductsResponse containing a list of products
        """
        pass

    @abstractmethod
    def cart_create(self, cart_input: CartCreateRequest) -> CartCreateResponse:
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
