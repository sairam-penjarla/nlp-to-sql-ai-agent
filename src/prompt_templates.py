COMPLETE_SCHEMA = """
asin: B0BQ118F2T, B0CV2W1TKZ, B09SM24S8C, B0CHH1N9VY, B09T3MQSVP, B0BZG14KFJ, B0C2SWQBMB, B0CTD47P22, B0CSB14R7J, B0CHK6LWKZ
product_title: Moto G Play 2023 3-Day Battery Unlocked Made for US 3/32GB 16MP Camera Navy Blue, Samsung Galaxy A15 (SM-155M/DSN), 128GB 6GB RAM, Dual SIM, Factory Unlocked GSM, International Version (Ring Grip Case Bundle) (Light Blue), Samsung Galaxy A03s Cell Phone, AT&amp;T GSM Unlocked Android Smartphone, 32GB, Long Lasting Battery, Expandable Storage, 3 Camera Lenses, Infinite Display - Black (Renewed), TracFone | Motorola Moto g Pure | Locked | 32GB | 4000 mAh Battery | 13 MP Dual Camera System | 6.5&quot; Max Vision HD+ Display | Blue, Samsung Galaxy A13 5G Cell Phone, AT&amp;T GSM Unlocked Android Smartphone, 64GB, Long Lasting Battery, Expandable Storage, Triple Lens Camera, Infinite Display, Black (Renewed)
product_price: 99.0, 153.99, 69.0, 49.99, 88.09, 149.99, 149.5, 139.99, 59.99, 89.0
product_original_price: 169.99, nan, 99.99, 98.27, 59.99, 249.99, 158.0, 299.99, 415.0, 44.7
currency: USD, nan
product_star_rating: 4.0, 4.2, 3.8, 4.4, 4.3, 4.1, 3.6, 3.9, 4.5, 3.3
product_num_ratings: 1319, 186, 597, 2814, 1338, 3843, 2637, 253, 573, 258
product_url: https://www.amazon.com/dp/B0BQ118F2T, https://www.amazon.com/dp/B0CV2W1TKZ, https://www.amazon.com/dp/B09SM24S8C, https://www.amazon.com/dp/B0CHH1N9VY, https://www.amazon.com/dp/B09T3MQSVP
product_photo: https://m.media-amazon.com/images/I/61K1Fz5LxvL._AC_UY654_FMwebp_QL65_.jpg, https://m.media-amazon.com/images/I/31bNhi6E3eL._AC_UY650_FMwebp_QL65_.jpg, https://m.media-amazon.com/images/I/51m45B3Yy+L._AC_UY654_FMwebp_QL65_.jpg, https://m.media-amazon.com/images/I/71zGrrAe5NL._AC_UY654_FMwebp_QL65_.jpg, https://m.media-amazon.com/images/I/61xhaqnlKPL._AC_UY654_FMwebp_QL65_.jpg
product_num_offers: 16, 4, 35, 3, 31, 8, 9, 15, 10, 2
product_minimum_offer_price: 69.88, 147.5, 64.99, 43.99, 70.4, 25.19, 100.72, 146.5, 136.62, 50.48
is_best_seller: False, True
is_amazon_choice: False, True
is_prime: True, False
product_availability: Only 1 left in stock - order soon., nan, Only 3 left in stock - order soon., Only 6 left in stock - order soon., Only 9 left in stock - order soon.
climate_pledge_friendly: False, True
sales_volume: 4000.0, 1000.0, 2000.0, 500.0, 400.0, 200.0, 3000.0, 300.0, 900.0, 50.0
delivery: FREE delivery Tue, Sep 24 Only 1 left in stock - order soon., FREE delivery Tue, Sep 24, FREE delivery Mon, Sep 30, FREE delivery Wed, Sep 25, FREE delivery Tue, Sep 24 on $35 of items shipped by Amazon
has_variations: False, True
unit_price: nan, $25.00, $23.55
unit_count: nan, 2.0, 5.0
coupon_text: nan, Save 10% with coupon, Save $4.00 with coupon, Save $14.00 with coupon, Save 5% with coupon, Save $17.00 with coupon, Save 15% with coupon, Save $10.00 with coupon, Save 18% with coupon, Save $40.00 with coupon
"""

##################################################################################################################################
COLUMN_GUIDELINES = """
You have been provided with a set of column names from a CSV file. 
Determine which column names are relevant for formulating a pandas SQL query based on the question provided below. 
Consider the terminology used in the question. 
Return solely the column names in a JSON format following this structure:
{"column_names":[
"has_variations",
"unit_count",
"is_best_seller",
"is_amazon_choice",
"sales_volume"
]}
Present the organized data strictly in the aforementioned JSON format—avoid any markdown formatting in your response.
"""

##################################################################################################################################
QUERY_GUIDELINES = """
Objective: As a pandas SQL assistant, your role is to construct accurate pandas SQL queries tailored to user specifications.
Guidelines:
1. Generate **one** pandas SQL query formatted in **Markdown**.
2. Begin the query with `SELECT` and wrap it in triple backticks (```` ``` ````).
3. Ensure that you use only the column names available in the provided schema. Avoid any invented data.
4. When addressing follow-up inquiries, reference the previous discussion, focusing closely on context around terms like "hazard" or questions aimed at "Site_name."
"""

##################################################################################################################################
AGENT_GUIDELINES = """
Objective: You are an AI chatbot tasked with helping users by providing answers to their inquiries using context derived from pandas SQL query results. Your goal is to convey information in a clear and natural manner, without discussing any technical aspects.
Instructions:
1. Consistently apply best practices for formatting, including headings, Tables, Bullet points and text organization.
2. Use the context obtained from the pandas SQL query results to formulate your responses, avoiding any reference to technical processes.
3. Ensure your replies are conversational and relatable, catering to users who may not be familiar with technical terminology.
4. Maintain a warm and supportive tone, making sure your responses are easily understandable for non-technical audiences.
5. Respond solely based on the provided data. Avoid speculation or introducing information not present in the data. Always verify that your answers are rooted in the given context.
"""