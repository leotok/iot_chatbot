from entities import predict_entities
from intent import predict_intent

def predict_message(msg):
    intent = predict_intent(msg)
    entities_described = predict_entities(msg)

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
    return intent, entities, entities_described