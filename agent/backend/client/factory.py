from agent.backend.client.base_types import StoreProvider
from agent.backend.client.interface import ProductsClient, StoreFrontClient
from agent.backend.client.shopify import ShopifyStoreFrontClient, ShopifyAdminClient


def get_storefront_client(provider: StoreProvider, **provider_kwargs) -> StoreFrontClient:
    if provider == StoreProvider.SHOPIFY:
        return ShopifyStoreFrontClient(
            store_url=provider_kwargs.get("store_url", ""),
            access_token=provider_kwargs.get("access_token"),
        )
    else:
        raise ValueError(f"Unsupported store provider: {provider}")

def get_products_client(provider: StoreProvider, **provider_kwargs) -> ProductsClient:
    if provider == StoreProvider.SHOPIFY:
        return ShopifyAdminClient(
            store_url=provider_kwargs.get("store_url", ""),
            access_token=provider_kwargs.get("access_token", ""),
        )
    else:
        raise ValueError(f"Unsupported store provider: {provider}")
