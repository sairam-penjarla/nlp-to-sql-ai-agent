import json
import os
import traceback

from flask import Flask, Response, jsonify, render_template, request

from custom_logger import logger
from src.prompt_templates import (
    AGENT_GUIDELINES,
    COLUMN_GUIDELINES,
    COMPLETE_SCHEMA,
    QUERY_GUIDELINES,
)
from src.utils import Utilities

app = Flask(__name__)
utils = Utilities()

@app.route("/")
def landing_page():
    try:
        logger.info("Landing page accessed")
        previous_session_meta_data = utils.session_utils.get_session_meta_data()
        logger.info("Fetched previous session meta data")
        return render_template(
            "index.html", previous_session_meta_data=previous_session_meta_data
        )
    except Exception:
        logger.error("Error in landing_page function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/get_random_session_icon", methods=["POST"])
def get_random_session_icon():
    try:
        logger.info("get_random_session_icon endpoint accessed")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        session_id = data.get("session_id")
        logger.info(f"Session ID: {session_id}")
        return jsonify({"relavant_schema": utils.get_session_icon(session_id)})
    except Exception:
        logger.error("Error in get_random_session_icon function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/extract_relavant_schema", methods=["POST"])
def extract_relavant_schema():
    try:
        logger.info("extract_relavant_schema endpoint accessed")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        user_input = data.get("user_input")
        logger.info(f"User input: {user_input}")

        msg = utils.get_user_msg(
            content=COLUMN_GUIDELINES + COMPLETE_SCHEMA,
            question=user_input,
        )
        logger.info(f"Generated message: {msg}")
        llm_output = utils.invoke_llm(messages=[msg])
        logger.info(f"LLM output: {llm_output}")
        relavant_schema = utils.get_relavant_schema(llm_output)
        logger.info(f"Relevant schema: {relavant_schema}")
        return jsonify({"relavant_schema": relavant_schema})

    except Exception:
        logger.error("Error in extract_relavant_schema function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/get_session_data", methods=["POST"])
def get_session_data():
    try:
        logger.info("get_session_data endpoint accessed")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        session_id = data.get("sessionId")
        logger.info(f"Session ID: {session_id}")
        session_data = utils.session_utils.get_session_data(session_id)
        logger.info(f"Session data: {session_data}")
        return jsonify({"session_data": session_data})

    except Exception:
        logger.error("Error in get_session_data function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/delete_session", methods=["POST"])
def delete_session():
    try:
        logger.info("delete_session endpoint accessed")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        session_id = data.get("session_id")
        logger.info(f"Session ID: {session_id}")

        if not session_id:
            logger.warning("Session ID is required")
            return jsonify({"error": "Session ID is required."}), 400

        response, status_code = utils.session_utils.delete_session(session_id)
        logger.info(f"Delete session response: {response}, status code: {status_code}")
        return jsonify(response), status_code

    except Exception:
        logger.error("Error in delete_session function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/delete_all_sessions", methods=["POST"])
def delete_all_sessions():
    try:
        logger.info("delete_all_sessions endpoint accessed")
        response, status_code = utils.session_utils.delete_all_sessions()
        logger.info(f"Delete all sessions response: {response}, status code: {status_code}")
        return jsonify(response), status_code

    except Exception:
        logger.error("Error in delete_all_sessions function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/update_session", methods=["POST"])
def update_session():
    try:
        logger.info("update_session endpoint accessed")
        data = request.get_json()
        logger.info(f"Received data: {data}")

        session_id = data.get("session_id")
        prompt = data.get("prompt")
        sql_query = data.get("sql_query")
        sql_data = data.get("sql_data")
        session_icon = data.get("session_icon")
        chatbot_assistant = data.get("chatbot_assistant")

        logger.info(f"Updating session with ID: {session_id}")
        utils.session_utils.add_data(
            session_id, prompt, sql_query, sql_data, chatbot_assistant, session_icon
        )
        logger.info("Session updated successfully")

        return jsonify({"success": True})

    except Exception:
        logger.error("Error in update_session function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/generate_sql_query", methods=["POST"])
def generate_sql_query():
    try:
        logger.info("generate_sql_query endpoint accessed")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        relavant_schema = data.get("relavant_schema")
        user_input = data.get("user_input")
        session_id = data.get("session_id")

        logger.info(f"Generating SQL query for session ID: {session_id}")
        messages = utils.get_previous_messages(
            session_id, QUERY_GUIDELINES, "sql_query"
        )
        msg = {
            "role": "user",
            "content": f"\n\nRelevant Schema:{relavant_schema}\n\nQuestion:{user_input}\n\nAnswer:",
        }

        llm_output = utils.invoke_llm_stream(messages + [msg])
        logger.info("SQL query generated successfully")
        return Response(llm_output, content_type="text/event-stream")

    except Exception:
        logger.error("Error in generate_sql_query function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/execute_sql_query", methods=["POST"])
def execute_sql_query():
    try:
        logger.info("execute_sql_query endpoint accessed")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        sql_query = data.get("sql_query")
        logger.info(f"SQL query: {sql_query}")
        # sql_query = utils.extract_query(sql_query)
        # logger.info(f"Extracted SQL query: {sql_query}")

        sql_data = utils.execute_query(sql_query)
        logger.info(f"SQL query executed successfully, data: {sql_data}")
        return jsonify({"sql_data": sql_data})

    except Exception:
        logger.error("Error in execute_sql_query function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/invoke_agent", methods=["POST"])
def invoke_agent():
    try:
        logger.info("invoke_agent endpoint accessed")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        sql_data = data.get("sql_data")
        user_input = data.get("user_input")
        session_id = data.get("session_id")

        logger.info(f"Invoking agent for session ID: {session_id}")
        messages = utils.get_previous_messages(
            session_id, AGENT_GUIDELINES, "chatbot_assistant"
        )
        msg = {
            "role": "user",
            "content": f"SQL Data:{sql_data}\n\nQuestion:{user_input}\n\nAnswer:",
        }

        agent_output = utils.invoke_llm_stream(messages=messages + [msg])
        logger.info("Agent invoked successfully")
        return Response(agent_output, content_type="text/event-stream")

    except Exception:
        logger.error("Error in invoke_agent function:")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500


if __name__ == "__main__":
    logger.info("Starting the Flask application")
    app.run(host="0.0.0.0", port=8000, debug=True)
