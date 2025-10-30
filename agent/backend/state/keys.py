"""
CART_STATE_KEY is the key used to store cart information in the ToolContext state in the following format:
@type: StateCart
"""
CART_STATE_KEY = "X-cart"


"""
@type: list[SearchCategory]
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
@type: Cart
"""
STORE_CART = "X-store-cart"


"""
A list of ProductSection objects stored in the ToolContext state
@type: list[ProductSection]
"""
PRODUCT_SECTIONS_STATE_KEY = "X-product-sections"
