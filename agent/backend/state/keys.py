"""
CART_STATE_KEY is the key used to store cart information in the ToolContext state in the following format:
{
    "item_id_1": quantity_1,
    "item_id_2": quantity_2,
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
TODO
"""
SHOPIFY_CART = "X-shopify-cart"


"""
a list of ProductSection objects stored in the ToolContext state
"""
PRODUCT_SECTIONS_STATE_KEY = "X-product-sections"
