"""
CART_STATE_KEY is the key used to store cart information in the ToolContext state in the following format:
{
    "item_id_1": {
        "quantity": 1,
        "title": title,
        "description": description,
        "image_url": image_url,
        "price": price,
    },
    "item_id_2": {
        "quantity": 1,
        "title": title,
        "description": description,
        "image_url": image_url,
        "price": price,
    },
    ...
}
"""
CART_STATE_KEY = "X-cart"


"""
[
    {
        "title": "hats",
        "subtitle": "Stylish Hats",
        "description": "A variety of stylish hats.",
        "query": "red hat",
    },
    {
        "title": "shoes",
        "subtitle": "Stylish Shoes",
        "description": "A variety of stylish shoes.",
        "query": "black shoe",
    },
    ...
]
"""
SEARCH_CATEGORIES_STATE_KEY = "X-search-categories"

"""
Store cart object stored in the ToolContext state
"""
STORE_CART = "X-store-cart"


"""
A list of ProductSection objects stored in the ToolContext state
@type: list[ProductSection]
"""
PRODUCT_SECTIONS_STATE_KEY = "X-product-sections"
