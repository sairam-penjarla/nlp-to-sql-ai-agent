import json
import os
import traceback

from flask import Flask, Response, jsonify, render_template, request

from custom_logger import logger
from src.multi_shot_examples import get_exmaples
from src.prompt_templates import (
    AGENT_GUIDELINES,
    COLUMN_GUIDELINES,
    COMPLETE_SCHEMA,
    QUERY_GUIDELINES,
)
from src.utils import Utilities

app = Flask(__name__)
utils = Utilities()

queries_conversation = get_exmaples("queries_conversation")
agent_conversation = get_exmaples("agent_conversation")


@app.route("/")
def landing_page():
    try:
        previous_session_meta_data = utils.session_utils.get_session_meta_data()
        return render_template(
            "index.html", previous_session_meta_data=previous_session_meta_data
        )
    except Exception:
        print("Error in landing_page function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/get_random_session_icon", methods=["POST"])
def get_random_session_icon():
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        return jsonify({"relavant_schema": utils.get_session_icon(session_id)})
    except Exception:
        print("Error in landing_page function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/extract_relavant_schema", methods=["POST"])
def extract_relavant_schema():
    try:
        data = request.get_json()
        user_input = data.get("user_input")

        msg = utils.get_user_msg(
            content=COLUMN_GUIDELINES + COMPLETE_SCHEMA,
            question=user_input,
        )
        llm_output = utils.invoke_llm(messages=[msg])
        relavant_schema = utils.get_relavant_schema(llm_output)
        return jsonify({"relavant_schema": relavant_schema})

    except Exception:
        print("Error in extract_relavant_schema function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/get_session_data", methods=["POST"])
def get_session_data():
    try:
        data = request.get_json()
        session_id = data.get("sessionId")
        session_data = utils.session_utils.get_session_data(session_id)
        return jsonify({"session_data": session_data})

    except Exception:
        print("Error in get_session_data function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/delete_session", methods=["POST"])
def delete_session():
    try:
        data = request.get_json()
        session_id = data.get("session_id")

        if not session_id:
            return jsonify({"error": "Session ID is required."}), 400

        response, status_code = utils.session_utils.delete_session(session_id)
        return jsonify(response), status_code

    except Exception:
        print("Error in delete_session function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/delete_all_sessions", methods=["POST"])
def delete_all_sessions():
    try:
        response, status_code = utils.session_utils.delete_all_sessions()
        return jsonify(response), status_code

    except Exception:
        print("Error in delete_all_sessions function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/update_session", methods=["POST"])
def update_session():
    try:
        data = request.get_json()

        session_id = data.get("session_id")
        prompt = data.get("prompt")
        sql_query = data.get("sql_query")
        session_icon = data.get("session_icon")
        chatbot_assistant = data.get("chatbot_assistant")

        utils.session_utils.add_data(
            session_id, prompt, sql_query, chatbot_assistant, session_icon
        )

        return jsonify({"success": True})

    except Exception:
        print("Error in update_session function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/generate_sql_query", methods=["POST"])
def generate_sql_query():
    try:
        data = request.get_json()
        relavant_schema = data.get("relavant_schema")
        user_input = data.get("user_input")
        session_id = data.get("session_id")

        # Retrieve previous messages for SQL query generation
        messages = utils.get_previous_messages(
            session_id, QUERY_GUIDELINES, "sql_query"
        )
        msg = {
            "role": "user",
            "content": f"\n\nRelevant Schema:{relavant_schema}\n\nQuestion:{user_input}\n\nAnswer:",
        }

        # Generate SQL query
        llm_output = utils.invoke_llm(messages + [msg])
        sql_query = utils.extract_query(llm_output)
        return jsonify({"sql_query": sql_query})

    except Exception:
        print("Error in generate_sql_query function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/execute_sql_query", methods=["POST"])
def execute_sql_query():
    try:
        data = request.get_json()
        sql_query = data.get("sql_query")

        # Execute the SQL query
        sql_data = utils.execute_query(sql_query)
        return jsonify({"sql_data": sql_data})

    except Exception:
        print("Error in execute_sql_query function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/invoke_agent", methods=["POST"])
def invoke_agent():
    try:
        data = request.get_json()
        sql_data = data.get("sql_data")
        user_input = data.get("user_input")
        session_id = data.get("session_id")

        # Retrieve previous messages for chatbot assistant
        messages = utils.get_previous_messages(
            session_id, AGENT_GUIDELINES, "chatbot_assistant"
        )
        msg = {
            "role": "user",
            "content": f"SQL Data:{sql_data}\n\nQuestion:{user_input}\n\nAnswer:",
        }

        # Stream the response from the LLM
        agent_output = utils.invoke_llm_stream(messages=messages + [msg])
        return Response(agent_output, content_type="text/event-stream")

    except Exception:
        print("Error in invoke_agent function:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
