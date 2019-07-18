import enum
import json
import datetime
import random
import requests
import unidecode


MODELS_API = 'http://localhost:5000/api/predict'

positive_words = {'sim', 'positivo', 'claro', 'pode ser', 'obvio', 'com certeza', 'pode ser', 'ok'}
negative_words = {'nao', 'negativo', 'errado', 'errou', 'nenhum'}
how_are_you_words = {'tudo bem?', 'como vai?', 'blz?', 'tudo certo?', 'tranquilo?'}
greetings_words = {'oi', 'ola', 'eai', 'eai', 'alo', 'oie'}
thanks_words = {'obrigado', 'agradecido', 'obrigada', 'agradecida', 'valeu'}
help_words = {'ajuda', 'help', 'duvida', 'comandos', 'o que', 'quais', 'qual', 'como'}
cancel_words = {'cancela', 'aborta', 'deixa', 'deixa pra la', 'nada', 'esquece', 'volta', 'ignora'}
bye_words = {'tchau', 'adeus', 'ate', 'ate mais', 'ate logo'}

initial_message = 'Olá, eu sou o Chatbot do Curso de Verão! Em que posso te ajudar?'
restart_message = 'Tudo bem... em que posso te ajudar?'
how_are_you_message = 'Beleza!'
thanks_message = 'De nada!'
bye_message = 'Tchau!'
help_message = '''
Fui treinado para te ajudar com as seguintes tarefas:
<br/><br/>
- Ligar um aparelho<br/>
Ex: 'Liga o ar condicionado.'<br/>
- Desligar um aparelho<br/>
Ex: 'Apaga a luz.'<br/>
- Criar uma regra<br/>
Ex: 'Ligue a cafeteira as 7am.'
<br/><br/>
O que deseja que eu faça?
'''

def get_devices():
    return  [
    {
        'device': 'Projetor',
        'location': 'Sala Paris',
    },
    {
        'device': 'Ar condicionado',
        'location': 'OLX',
    },
    {
        'device': 'Televisão',
        'location': 'Sala Paris',
    },
    {
        'device': 'Luz',
        'location': 'Sala Paris',
    },
    {
        'device': 'Cafeteira',
        'location': 'Copa',
    },
]

class ChatStates(enum.Enum):
    nenhum = 0
    ligar = 1
    confirmar_ligar = 2
    desligar = 3
    confirmar_desligar = 4
    criar_regra = 5

class Acao(enum.Enum):
    ligar = 0
    desligar = 1
    criar_regra = 2

chat_context = {'state': ChatStates.nenhum}

def process_text(text):
    text = unidecode.unidecode(text)
    return text.lower()

def answer(text):
    return {'error': 0, 'bot_message': text[0].capitalize() + text[1:]}

def set_chat_context(state, device=None):
    global chat_context
    chat_context = {'state': state, 'device': device}

def search_device(text):
    return [d for d in get_devices() if text.lower() in d['device'].lower() or text.lower() in d['location'].lower()]

def handler_more_than_one_device_search(user_message, devices):
    devices_list = '<br/>'.join(['- ' + d['device'] + ': ' + d['location'] for d in devices])
    return 'Qual destes é o aparelho {}?<br/>{}'.format(user_message, devices_list)

def handle_priority_expressions(user_message):
    if user_message in greetings_words:
        set_chat_context(ChatStates.nenhum)
        return random.choice(list(greetings_words))
    elif user_message in thanks_words:
        set_chat_context(ChatStates.nenhum)
        return thanks_message
    elif user_message in cancel_words:
        set_chat_context(ChatStates.nenhum)
        return restart_message
    elif user_message in bye_words:
        set_chat_context(ChatStates.nenhum)
        return bye_message
    elif user_message in how_are_you_words:
        set_chat_context(ChatStates.nenhum)
        return how_are_you_message
    elif [True for w in help_words if w in user_message]:
        set_chat_context(ChatStates.nenhum)
        return help_message

def handle_user_chat_context(user_message):
    actual_context = chat_context
    if actual_context.get('state') == ChatStates.nenhum:
        return None
    if actual_context.get('state') == ChatStates.confirmar_ligar:
        if user_message in positive_words and actual_context.get('device'):
            device = actual_context.get('device')
            set_chat_context(ChatStates.nenhum)
            return 'Ligando {}: {}'.format(device['device'], device['location'])
        elif user_message in negative_words:
            set_chat_context(ChatStates.nenhum)
            return 'Engano meu. O que deseja fazer?'

    elif actual_context.get('state') == ChatStates.confirmar_desligar:
        if user_message in positive_words and actual_context.get('device'):
            device = actual_context.get('device')
            set_chat_context(ChatStates.nenhum)
            return 'Desligando {}: {}'.format(device['device'], device['location'])
        elif user_message in negative_words:
            set_chat_context(ChatStates.nenhum)
            return 'Engano meu. O que deseja fazer?'

    elif actual_context.get('state') == ChatStates.ligar or actual_context.get('state') == ChatStates.desligar:
        devices = search_device(user_message)
        if len(devices) == 1:
            device = devices[0]
            if actual_context.get('state') == ChatStates.ligar:
                set_chat_context(ChatStates.confirmar_ligar, device=device)
                bot_answer = 'Deseja ligar o aparelho {}: {}?'.format(device['device'], device['location'])
            elif actual_context.get('state') == ChatStates.desligar:
                set_chat_context(ChatStates.confirmar_desligar, device=device)
                bot_answer = 'Deseja desligar o aparelho {}: {}?'.format(device['device'], device['location'])
            return bot_answer
        elif len(devices) > 1:
            return handler_more_than_one_device_search(user_message, devices)
        else:
            return 'Desculpe, não entendi... Qual aparelho?'

def get_message_interpretation(user_message):
    response = requests.post(MODELS_API, data={'cmd': user_message}).json()
    intent = max(response.get('intent'), key=lambda x: x[1])[0]
    entities = response.get('entities')
    return intent, entities

def handle_user_intent(intent, entities, user_message):
    bot_answer = ''
    if intent == 'ligar_um_aparelho':
        if len(entities) == 1:
            devices = search_device(entities[0])
            if len(devices) == 1:
                device = devices[0]
                bot_answer = 'Deseja ligar o aparelho {}: {}?'.format(device['device'], device['location'])
                set_chat_context(ChatStates.confirmar_ligar, device=device)
            elif len(devices) > 1:
                set_chat_context(ChatStates.ligar)
                bot_answer = handler_more_than_one_device_search(entities[0], devices)
            else:
                bot_answer = 'Desculpe, mas não encontrei o aparelho {}'.format(entities[0])
                set_chat_context(ChatStates.nenhum)
        else:
            set_chat_context(ChatStates.ligar)
            devices_list = '<br/>'.join(['- ' + d['device'] + ': ' + d['location'] for d in get_devices()])
            bot_answer = 'Qual aparelho deseja ligar?<br/>{}'.format(devices_list)
    elif intent == 'desligar_um_aparelho':
        if len(entities) == 1:
            devices = search_device(entities[0])
            if len(devices) == 1:
                device = devices[0]
                bot_answer = 'Deseja desligar o aparelho {}: {}?'.format(device['device'], device['location'])
                set_chat_context(ChatStates.confirmar_desligar, device=device)
            elif len(devices) > 1:
                set_chat_context(ChatStates.desligar)
                bot_answer = handler_more_than_one_device_search(entities[0], devices)
            else:
                bot_answer = 'Desculpe, mas não encontrei o aparelho {}'.format(entities[0])
                set_chat_context(ChatStates.nenhum)
        else:
            set_chat_context(ChatStates.desligar)
            devices_list = '<br/>'.join(['- ' + d['device'] + ': ' + d['location'] for d in get_devices()])
            bot_answer = 'Qual aparelho deseja desligar?<br/>{}'.format(devices_list)
    elif intent == 'criar_regra':
        bot_answer = 'Qual regra deseja criar?'
    return bot_answer
