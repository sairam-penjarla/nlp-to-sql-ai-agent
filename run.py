from src.utils import Utilities
from flask import (
    Flask, 
    Response, 
    jsonify, 
    render_template, 
    request
)
from src.prompt_templates import ( 
    COMPLETE_SCHEMA, 
    COLUMN_GUIDELINES
)

app = Flask(__name__)
utils = Utilities()

agent_conversation = utils.get_default_conversation(is_agent = True)
queries_conversation = utils.get_default_conversation(is_agent = False)

@app.route("/")
def landing_page():
    return render_template("index.html")

@app.route('/extract_relavant_schema', methods=['POST'])
def extract_relavant_schema():
    data = request.get_json()
    user_input = data.get('user_input')

    msg = utils.get_user_msg( 
            content = COLUMN_GUIDELINES + COMPLETE_SCHEMA, 
            conversations = agent_conversation, 
            present_question = user_input, 
        )
    llm_output = utils.invoke_llm(conversations = [msg])
    RELAVANT_SCHEMA = utils.get_relavant_schema(llm_output)

    return jsonify({"relavant_schema" : RELAVANT_SCHEMA})

@app.route('/gather_sql_content', methods=['POST'])
def gather_sql_content():
    data = request.get_json()

    RELAVANT_SCHEMA = data.get('relavant_schema')
    user_input = data.get('user_input')

    msg = utils.get_user_msg( 
                content = RELAVANT_SCHEMA, 
                conversations = queries_conversation, 
                present_question = user_input, 
            )
    llm_output = utils.invoke_llm(conversations = queries_conversation + [msg])
    query = utils.extract_query(llm_output)
    df = utils.execute_query(query)
    SQL_CONTENT = utils.get_sql_content(df)

    return jsonify({"sql_content" : SQL_CONTENT})


@app.route('/invoke_agent', methods=['POST'])
def invoke_agent():
    data = request.get_json()

    SQL_CONTENT = data.get('sql_content')
    user_input = data.get('user_input')

    msg = utils.get_user_msg( 
                content = SQL_CONTENT, 
                conversations = agent_conversation, 
                present_question = user_input, 
            )
    agent_output = utils.invoke_llm_stream(conversations = agent_conversation + [msg])

    return Response(agent_output, content_type='text/event-stream')


@app.route('/markdown_to_html', methods=['POST'])
def markdown_to_html():
    return jsonify({"agent_output" : utils.markdown_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)