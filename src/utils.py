import os
from openai import OpenAI
from custom_logger import logger
from config import get_config
from dotenv import load_dotenv
from src.session_utils import SessionUtilities
from src.multi_shot_examples import get_exmaples
import os
import json
import re
import pandasql as ps
import pandas as pd
from src.prompt_templates import COMPLETE_SCHEMA
import random

df = pd.read_csv("dataset/cleaned_phone_search_data.csv")

load_dotenv()

class Utilities:
    def __init__(self):
        logger.debug("initializing utilities")
        self.config = get_config()
        self.session_utils = SessionUtilities()

        self.client = OpenAI()

    def get_user_msg(self, 
                     content, 
                     question, 
                    ):
        logger.debug("getting user message")

        return {
            "role": "user",
            "content": f"Content:{content}\n\nQuestion:{question}\n\nAnswer:",
        }
    
    def get_session_icon(self, session_id):
        icon_name = self.session_utils.get_session_icon(session_id)
        if icon_name is None:
            icons_dir_path = "static/images/session-icons"
            random_icon = random.choice([x for x in os.listdir(icons_dir_path) if x.endswith(".svg")])
            return random_icon
        return icon_name
    
    def get_relavant_schema(self, llm_output):
        logger.debug("getting relavant schema")
        json_data = json.loads(llm_output)
        RELAVANT_SCHEMA = []
        for col in json_data["column_names"]:
            for line in COMPLETE_SCHEMA.split("\n"):
                if line.startswith(col):
                    RELAVANT_SCHEMA.append(line)
                    break
        if RELAVANT_SCHEMA == []:
            RELAVANT_SCHEMA = ['Answer this question in general.']
        return "\n".join(RELAVANT_SCHEMA)
    
    def extract_query(self, llm_output):
        logger.debug("extracting query")
        pattern = r'```(.*?)```'
        match = re.search(pattern, llm_output, re.DOTALL)
        if match:
            query = match.group(1).strip()
            query = query.strip("sql").strip("\n")
            return query
        
    
    def execute_query(self, query):
        logger.debug("executing query")
        if query:
            # Execute the query and get the result as a DataFrame
            result_df = ps.sqldf(query)

            # Convert the DataFrame to a JSON-formatted string
            result_json = result_df.to_json(orient="records")

            return result_json
        else:
            return json.dumps({"error": "No query provided"})

    
    def get_sql_content(self, df):
        logger.debug("getting sql content")
        sql_content = str(df.to_dict(orient="records")).encode("utf-8", errors="ignore").decode("utf-8")
        return sql_content
        
    def get_previous_messages(self, session_id, instructions, component):
        session_data = self.session_utils.get_session_data(session_id)
        messages = [{
                    "role": "system",
                    "content": instructions
                }]
        messages += get_exmaples(instructions)
        for request in session_data:
            messages.append(
                {
                    "role": "user",
                    "content": request['prompt']
                }
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": str(request[component])
                }
            )
        return messages

    def invoke_llm(self, messages):
        llm_params = self.config.LLM_PARAMS
        llm_params['messages'] = messages
        llm_params['stream'] = False

        chat_completion = self.client.chat.completions.create(
            **llm_params
        )
        
        return chat_completion.choices[0].message.content
    
    def invoke_llm_stream(self, messages):
        logger.debug("invoking llm")
        llm_params = self.config.LLM_PARAMS
        llm_params['messages'] = messages
        llm_params['stream'] = True

        chat_completion = self.client.chat.completions.create(
            **llm_params
        )

        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                yield content