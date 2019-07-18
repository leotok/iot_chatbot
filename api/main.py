from flask import Flask, jsonify, request, render_template, redirect, url_for
from entities import predict_entities
from intent import predict_intent
from chatbot import process_text, answer, get_message_interpretation
from chatbot import handle_user_chat_context, handle_user_intent, handle_priority_expressions


app = Flask(__name__)

@app.route('/models')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chat.html')

@app.route('/api/predict', methods=['POST'])
def predict_view():
    cmd = request.form.get('cmd')
    intent = predict_intent(cmd)
    entities_described = predict_entities(cmd)

    prev_ent = None
    full_ent = ''
    entities = []
    for i, e in enumerate(entities_described):
        if e['entity'] == 'B-DEVICE':
            full_ent = e['word']
        elif prev_ent and prev_ent['entity'] == 'B-DEVICE' and e['entity'] == 'I-DEVICE':
            full_ent += ' ' + e['word']
        elif e['entity'] == 'o':
            if prev_ent and (prev_ent['entity'] == 'B-DEVICE' or prev_ent['entity'] == 'I-DEVICE'):
                entities.append(full_ent)
            full_ent = ''
        prev_ent = e
    if prev_ent and (prev_ent['entity'] == 'B-DEVICE' or prev_ent['entity'] == 'I-DEVICE'):
        entities.append(full_ent)
            

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
