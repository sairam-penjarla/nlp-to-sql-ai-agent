from src.prompt_templates import COMPLETE_SCHEMA, QUERY_GUIDELINES, AGENT_GUIDELINES

query_guidelines = [
                # Example 1
                {
                    "role": "user",
                    "content": "Question: What is the average product price for items listed as best sellers? Answer:",
                },
                {
                    "role": "assistant",
                    "content": "```sql\nSELECT AVG(product_price) AS avg_best_seller_price FROM df WHERE is_best_seller = True;```",
                },
                # Example 2
                {
                    "role": "user",
                    "content": "Question: How many products are available for sale with a rating higher than 4.0? Answer:",
                },
                {
                    "role": "assistant",
                    "content": "```sql\nSELECT COUNT(*) AS num_products FROM df WHERE product_star_rating > 4.0;```",
                },
                # Example 3
                {
                    "role": "user",
                    "content": "Question: Which product has the highest sales volume? Answer:",
                },
                {
                    "role": "assistant",
                    "content": "```sql\nSELECT product_title, sales_volume FROM df ORDER BY sales_volume DESC LIMIT 1;```",
                },
                # Example 4
                {
                    "role": "user",
                    "content": "Question: What are the distinct product titles available for products that are Amazon Choice? Answer:",
                },
                {
                    "role": "assistant",
                    "content": "```sql\nSELECT DISTINCT product_title FROM df WHERE is_amazon_choice = True;```",
                },
                # Example 5
                {
                    "role": "user",
                    "content": "Question: What is the minimum offer price for products that have variations? Answer:",
                },
                {
                    "role": "assistant",
                    "content": "```sql\nSELECT MIN(product_minimum_offer_price) AS min_offer_price FROM df WHERE has_variations = True;```",
                }
            ]



agent_guidelines = []

def get_exmaples(component):
    if component == QUERY_GUIDELINES:
        return query_guidelines
    else:
        return agent_guidelines