import json
import os
import random
import re
import sqlite3

import pandas as pd
import pandasql as ps
from dotenv import load_dotenv
from openai import OpenAI

from config import get_config
from custom_logger import logger
from src.multi_shot_examples import get_exmaples
from src.prompt_templates import COMPLETE_SCHEMA
from src.session_utils import SessionUtilities


load_dotenv()


class Utilities:
    def __init__(self):
        logger.debug("initializing utilities")
        self.config = get_config()
        self.session_utils = SessionUtilities()

        self.client = OpenAI()

    def get_user_msg(
        self,
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
            random_icon = random.choice(
                [x for x in os.listdir(icons_dir_path) if x.endswith(".svg")]
            )
            return random_icon
        return icon_name

    def extract_query(self, llm_output):
        logger.debug("extracting query")
        pattern = r"```(.*?)```"
        match = re.search(pattern, llm_output, re.DOTALL)
        if match:
            query = match.group(1).strip()
            query = query.strip("sql").strip("\n")
            return query

    def execute_query(self, query):
        logger.debug("executing query")
        if query:
            conn = sqlite3.connect("dataset/inventory.db")
            try:
                if query.strip().lower().startswith("select"):
                    df = pd.read_sql_query(query, conn)
                else:
                    conn.execute(query)
                    conn.commit()
                    df = pd.DataFrame({"Status": ["Query executed successfully"]})
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                df = pd.DataFrame({"Error": [str(e)]})
            finally:
                conn.close()
            
            result_markdown = df.to_markdown(index=False)
            return result_markdown
        else:
            return "|   |   |\n|---|---|\n"

    def get_sql_content(self, df):
        logger.debug("getting sql content")
        sql_content = (
            str(df.to_dict(orient="records"))
            .encode("utf-8", errors="ignore")
            .decode("utf-8")
        )
        return sql_content

    def get_previous_messages(self, session_id, instructions, component):
        session_data = self.session_utils.get_session_data(session_id)
        messages = [{"role": "system", "content": instructions}]
        messages += get_exmaples(instructions)
        for request in session_data:
            messages.append({"role": "user", "content": request["prompt"]})
            messages.append({"role": "assistant", "content": str(request[component])})
        return messages

    def invoke_llm(self, messages):
        llm_params = self.config.LLM_PARAMS
        llm_params["messages"] = messages
        llm_params["stream"] = False

        chat_completion = self.client.chat.completions.create(**llm_params)

        return chat_completion.choices[0].message.content

    def invoke_llm_stream(self, messages):
        logger.debug("invoking llm")
        llm_params = self.config.LLM_PARAMS
        llm_params["messages"] = messages
        llm_params["stream"] = True

        chat_completion = self.client.chat.completions.create(**llm_params)

        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                yield content
