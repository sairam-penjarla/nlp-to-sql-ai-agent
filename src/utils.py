import os
import re
import json
import markdown
import pandas as pd
from openai import OpenAI
from config import get_config
from logger import logger
from src.prompt_templates import COMPLETE_SCHEMA, QUERY_GUIDELINES, AGENT_GUIDELINES
import pandasql as ps
from dotenv import load_dotenv

load_dotenv()

df = pd.read_csv("dataset/cleaned_phone_search_data.csv")


class Utilities:
    def __init__(self):
        logger.debug("initializing utilities")
        self.config = get_config()

        self.DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
        self.DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")

        self.client = OpenAI(
            api_key = self.DATABRICKS_TOKEN,
            base_url = f"{self.DATABRICKS_HOST}/serving-endpoints"
        )
    
    def get_default_conversation(self, is_agent):
        logger.debug("getting default conversations")
        if is_agent :
            return [
                {
                "role": "system",
                "content": AGENT_GUIDELINES
                },]
        else:
            return [
                {
                    "role": "system",
                    "content": QUERY_GUIDELINES
                },
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

    
    def get_user_msg(self, 
                     content, 
                     conversations, 
                     present_question, 
                     previous_question="", 
                     previous_answer=""
                    ):
        logger.debug("getting user message")
        if len(conversations) > 1:
            previous_question = "Previous Question: " + conversations[-2]['content']
            previous_answer = "Previous Answer: " + conversations[-1]['content']

        return {
            "role": "user",
            "content": f"Content:{content}\n\n{previous_question}\n\n{previous_answer}\n\nQuestion:{present_question}\n\nAnswer:",
        }

    def get_relavant_schema(self, llm_output):
        logger.debug("getting relavant schema")
        json_data = json.loads(llm_output)
        RELAVANT_SCHEMA = []
        for col in json_data["column_names"]:
            for line in COMPLETE_SCHEMA.split("\n"):
                if line.startswith(col):
                    RELAVANT_SCHEMA.append(line)
                    break
        return "\n".join(RELAVANT_SCHEMA)

    def extract_query(self, llm_output):
        logger.debug("extracting query")
        print(llm_output)
        pattern = r'```(.*?)```'
        match = re.search(pattern, llm_output, re.DOTALL)
        if match:
            query = match.group(1).strip()
            query = query.strip("sql").strip("\n")
            return query
        else:
            raise "There is no query present in llm output"
    
    def execute_query(self, query):
        logger.debug("executing query")
        return ps.sqldf(query)
    
    def get_sql_content(self, df):
        logger.debug("getting sql content")
        sql_content = str(df.to_dict(orient="records")).encode("utf-8", errors="ignore").decode("utf-8")
        return sql_content

    def dataframe_to_html(self, df):
        logger.debug("converting dataframe to html")
        if isinstance(df, pd.DataFrame):
            html = """
            <table class="sql-table">
                <thead>
                    <tr>
            """
            for col in df.columns:
                html += f"<th>{col}</th>"
            
            html += """
                    </tr>
                </thead>
                <tbody>
            """
            for index, row in df.iterrows():
                html += "<tr>"
                for value in row:
                    html += f"<td>{value}</td>"
                html += "</tr>"
            html += """
                </tbody>
            </table>
            """
        else:
            html = ""
        return html

    def markdown_to_html(self, markdown_text):
        logger.debug("converting markdown to html")
        self.markdown_text = markdown.markdown(markdown_text, extensions=['tables'])
    
    
    def invoke_llm(self, conversations):
        logger.debug("invoking llm")
        llm_params = self.config.LLM_PARAMS
        llm_params['messages'] = conversations
        llm_params['stream'] = False

        chat_completion = self.client.chat.completions.create(
            **llm_params
        )
        
        return chat_completion.choices[0].message.content

    def invoke_llm_stream(self, conversations):
        logger.debug("invoking llm")
        llm_params = self.config.LLM_PARAMS
        llm_params['messages'] = conversations
        llm_params['stream'] = True

        chat_completion = self.client.chat.completions.create(
            **llm_params
        )

        markdown_text = ""
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                markdown_text+=content
                yield f"data: {content}\n\n"
        
        self.markdown_to_html(markdown_text)
        yield "data: [DONE]\n\n"