import nltk
import os
import pandas as pd
import pickle
import unidecode

base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, 'models')
intent_model_path = os.path.join(models_dir, 'intent_model_02-03-2018.sav')

with open(intent_model_path, 'rb') as f:
  intent_model = pickle.load(f)

nltk.download('rslp')
stemmer = nltk.stem.RSLPStemmer()

labels_list = ['criar_regra', 'desligar_um_aparelho', 'ligar_um_aparelho']

def predict_intent(sent):
  sent = sent.lower()
  sent = unidecode.unidecode(sent)
  sent = ' '.join([stemmer.stem(s) for s in sent.split(' ')])

  predictions = intent_model.predict_proba([sent]).tolist()[0]
  return list(zip(labels_list, predictions))
  # return labels_list[intent_model.predict([sent])[0]]