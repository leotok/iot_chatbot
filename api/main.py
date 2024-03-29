from flask import Flask, jsonify, request, render_template, redirect, url_for
from models import predict_message
from chatbot import process_text, answer, get_message_interpretation
from chatbot import handle_user_chat_context, handle_user_intent, handle_priority_expressions


app = Flask(__name__)

@app.route('/')
def index_page():
    return '''
    <h2>Index</h2>
    <ol>
        <li><a target="_blank" href="/models">Sandbox modelos de intenção e entidades</a></li>
        <li><a target="_blank" href="/chatbot">Chatbot</a></li>
        <li><a target="_blank" href="localhost:8888">Jupyter Notebook</a></li>
    </ol>
    '''
    
@app.route('/models')
def models_page():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot_page():
    return render_template('chat.html')

@app.route('/api/predict', methods=['POST'])
def predict_endpoint():
    cmd = request.form.get('cmd')
    intent, entities, entities_described = predict_message(cmd)
    return jsonify({
        'sentence': cmd,
        'intent': intent,
        'entities': entities,
        'entities_described': entities_described,
    })

# Chatbot

@app.route('/api/chatbot/message', methods=['POST'])
def handle_chat_message():
    user_message = process_text(request.form.get('user_message'))
    if user_message is None or user_message == '':
        return 'User message should not be empty', 400
    
    bot_answer = handle_priority_expressions(user_message)
    if bot_answer is not None:
        return jsonify(answer(bot_answer))

    bot_answer = handle_user_chat_context(user_message)
    if bot_answer is not None:
        return jsonify(answer(bot_answer))

    intent, entities = get_message_interpretation(user_message)
    bot_answer = handle_user_intent(intent, entities, user_message)

    return jsonify(answer(bot_answer))


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.    
    app.run(debug=True,host='0.0.0.0')
