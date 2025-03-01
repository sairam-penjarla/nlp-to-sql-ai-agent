COMPLETE_SCHEMA = """{
    "item_id": {
        "description": "Unique identifier for each inventory item.",
        "examples": [1, 2, 3, 4, 5]
    },
    "item_name": {
        "description": "Name of the product stored in the inventory.",
        "examples": ["Laptop", "Office Chair", "Wireless Mouse", "Projector", "Coffee Machine"]
    },
    "category": {
        "description": "The category to which the product belongs.",
        "examples": ["Electronics", "Furniture", "Stationery", "Kitchen Appliances", "Automobile Accessories"]
    },
    "quantity": {
        "description": "Number of available units of the product in stock.",
        "examples": [10, 25, 5, 50, 100]
    },
    "price_per_unit": {
        "description": "Price of one unit of the product.",
        "examples": [75000, 5000, 1500, 30000, 12000]
    },
    "supplier": {
        "description": "The company or person supplying the product.",
        "examples": ["ABC Electronics", "XYZ Furniture", "Tech Supplies Co.", "Home Essentials Ltd.", "AutoParts Inc."]
    },
    "purchase_date": {
        "description": "The date on which the product was purchased.",
        "examples": ["2024-01-15", "2024-02-01", "2023-12-10", "2024-03-05", "2023-11-20"]
    },
    "expiry_date": {
        "description": "Expiry date for perishable items or warranty expiration for non-perishable items (NULL if not applicable).",
        "examples": ["2025-01-15", None, "2024-12-31", "2026-03-01", None]
    },
    "warehouse_location": {
        "description": "The physical storage location of the product.",
        "examples": ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad"]
    },
    "stock_status": {
        "description": "Indicates whether the product is in stock or out of stock.",
        "examples": ["In Stock", "Out of Stock", "Low Stock", "Pre-Order", "Discontinued"]
    }
}"""


##################################################################################################################################
QUERY_GUIDELINES = """
## Task:
You are an SQL assistant, your role is to construct accurate SQL queries tailored to user specifications.
You will be presented with the schema of the database and the user requirements. 
Your goal is to generate the appropriate SQL query as per the user request.

## Guidelines:
- Generate an SQL query.
- Ensure that you use only the column names available in the provided schema. Avoid any invented or made up data.
- Do not give any explanations, headings, comments, etc. Jus the query alone. nothing else.
"""

##################################################################################################################################
AGENT_GUIDELINES = """
##  Task: 
You are an AI chatbot tasked with helping users by providing answers to their inquiries using context derived from SQL query results. 
Your goal is to convey information in a clear and natural manner, without discussing any technical aspects.

## Guidelines:
- Consistently apply best practices for formatting, including headings, Tables, Bullet points and text organization.
- Use the context obtained from the SQL query results to formulate your responses, avoiding any reference to technical processes.
- Ensure your replies are conversational and relatable, catering to users who may not be familiar with technical terminology.
- Maintain a warm and supportive tone, making sure your responses are easily understandable for non-technical audiences.
- Respond solely based on the provided data. Avoid speculation or introducing information not present in the data. 
- Always verify that your answers are rooted in the given context.
"""