from src.prompt_templates import COMPLETE_SCHEMA, QUERY_GUIDELINES, AGENT_GUIDELINES

query_guidelines = [
    # Example 1
    {
        "role": "user",
        "content": "Question: Which items in the inventory belong to the 'Electronics' category and have a quantity greater than 5? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT item_id, item_name, category, quantity, price_per_unit, supplier FROM inventory WHERE category = 'Electronics' AND quantity > 5;",
    },

    # Example 2
    {
        "role": "user",
        "content": "Question: What is the total value of all inventory items (quantity * price per unit)? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT SUM(quantity * price_per_unit) AS total_inventory_value FROM inventory;",
    },

    # Example 3
    {
        "role": "user",
        "content": "Question: How many unique categories of products are available in the inventory? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT COUNT(DISTINCT category) AS unique_categories FROM inventory;",
    },

    # Example 4
    {
        "role": "user",
        "content": "Question: Which supplier provides the most number of different products? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT supplier, COUNT(DISTINCT item_id) AS product_count FROM inventory GROUP BY supplier ORDER BY product_count DESC LIMIT 1;",
    },

    # Example 5
    {
        "role": "user",
        "content": "Question: List all products that are out of stock. Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT item_id, item_name FROM inventory WHERE stock_status = 'Out of Stock' OR quantity = 0;",
    },

    # Example 6
    {
        "role": "user",
        "content": "Question: What is the average price per unit for each product category? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT category, AVG(price_per_unit) AS avg_price FROM inventory GROUP BY category;",
    },

    # Example 7
    {
        "role": "user",
        "content": "Question: What are the top 3 most expensive items in the inventory? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT item_id, item_name, price_per_unit FROM inventory ORDER BY price_per_unit DESC LIMIT 3;",
    },

    # Example 8
    {
        "role": "user",
        "content": "Question: How many items have an expiry date set? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT COUNT(*) AS items_with_expiry FROM inventory WHERE expiry_date IS NOT NULL;",
    },

    # Example 9
    {
        "role": "user",
        "content": "Question: Which warehouse location has the highest number of products stored? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT warehouse_location, COUNT(item_id) AS total_products FROM inventory GROUP BY warehouse_location ORDER BY total_products DESC LIMIT 1;",
    },

    # Example 10
    {
        "role": "user",
        "content": "Question: What is the total number of items supplied by 'ABC Electronics'? Answer:",
    },
    {
        "role": "assistant",
        "content": "SELECT SUM(quantity) AS total_items_supplied FROM inventory WHERE supplier = 'ABC Electronics';",
    }
]



agent_guidelines = []

def get_exmaples(component):
    if component == QUERY_GUIDELINES:
        return query_guidelines
    else:
        return agent_guidelines