import os
import tempfile
from dotenv import load_dotenv
from google.auth import default
import vertexai
from vertexai.preview import rag
from agent.backend.client.factory import get_storefront_client
from agent.backend.client.base_types import StoreProvider

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
CORPUS_DISPLAY_NAME = os.getenv("VERTEX_RAG_CORPUS", "Shopify_Products")
STORE_URL = os.getenv("SHOPIFY_STOREFRONT_URL")


def init_vertex():
    creds, _ = default()
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=creds)


def get_or_create_corpus():
    cfg = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )
    for c in rag.list_corpora():
        if c.display_name == CORPUS_DISPLAY_NAME:
            return c
    return rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description="Shopify product catalog",
        embedding_model_config=cfg,
    )


def to_rag_docs(get_products_response):
    texts = []
    for p in get_products_response.products:
        title = p.title or ""
        description = p.description or ""
        url = p.online_store_url or ""
        price = f"{p.price.amount} {p.price.currency_code}" if p.price else "N/A"
        images = ", ".join(p.images or [])
        variants = ", ".join([v.title for v in p.variants]) if p.variants else ""

        text = (
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Price: {price}\n"
            f"Variants: {variants}\n"
            f"URL: {url}\n"
            f"Images: {images}"
        ).strip()
        texts.append(text)
    return "\n\n---\n\n".join(texts)


def upload_to_rag(corpus, combined_text):
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        tmp.write(combined_text)
        tmp.flush()
        rag.upload_file(
            corpus_name=corpus.name,
            path=tmp.name,
            display_name="Shopify_All_Products",
            description="Combined Shopify product catalog",
        )


def main():
    if not all([PROJECT_ID, LOCATION, STORE_URL]):
        raise RuntimeError(
            "Missing env: GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, SHOPIFY_STOREFRONT_URL"
        )

    client = get_storefront_client(StoreProvider.SHOPIFY, store_url=STORE_URL)
    products = client.fetch_all_products()
    combined_text = to_rag_docs(products)

    init_vertex()
    corpus = get_or_create_corpus()
    upload_to_rag(corpus, combined_text)

    print(
        f"Uploaded {len(products.products)} products as one document to corpus '{corpus.display_name}'."
    )


if __name__ == "__main__":
    main()