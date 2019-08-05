import os
import pandas as pd
import pickle
import warnings
from sklearn import preprocessing
import spacy
import pt_core_news_sm

warnings.filterwarnings("ignore", category=DeprecationWarning)

entities_model_path = 'models/entities_model_02-03-2018.sav'
entities_label_binarizer_model_path = 'models/entities_label_binarizer.sav'

with open(entities_model_path, 'rb') as f:
  entities_model = pickle.load(f)

# nlp = spacy.load('pt_core_news_sm')
nlp = pt_core_news_sm.load()

with open(entities_label_binarizer_model_path, 'rb') as f:
  labels_encoder = pickle.load(f)

columns=['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'label']
features_columns = [
    'f1_ADJ', 'f1_ADP', 'f1_ADV', 'f1_AUX', 'f1_CCONJ',
    'f1_DET', 'f1_NOUN', 'f1_NUM', 'f1_PRON', 'f1_PROPN',
    'f1_PUNCT', 'f1_SCONJ', 'f1_START', 'f1_SYM', 'f1_VERB',
    'f1_X', 'f2_ADJ', 'f2_ADP', 'f2_ADV', 'f2_AUX', 'f2_CCONJ',
    'f2_DET', 'f2_NOUN', 'f2_NUM', 'f2_PRON', 'f2_PROPN',
    'f2_PUNCT', 'f2_SCONJ', 'f2_START', 'f2_SYM', 'f2_VERB',
    'f2_X', 'f3_ADJ', 'f3_ADP', 'f3_ADV', 'f3_AUX', 'f3_CCONJ',
    'f3_DET', 'f3_NOUN', 'f3_NUM', 'f3_PRON', 'f3_PROPN', 
    'f3_PUNCT', 'f3_SCONJ', 'f3_START', 'f3_SYM', 'f3_VERB', 
    'f3_X', 'f4_ADJ', 'f4_ADP', 'f4_ADV', 'f4_AUX', 'f4_CCONJ',
    'f4_DET', 'f4_NOUN', 'f4_NUM', 'f4_PRON', 'f4_PROPN',
    'f4_PUNCT', 'f4_SCONJ', 'f4_SYM', 'f4_VERB', 'f4_X',
    'f5_ADJ', 'f5_ADP', 'f5_ADV', 'f5_AUX', 'f5_CCONJ',
    'f5_DET', 'f5_END', 'f5_NOUN', 'f5_NUM', 'f5_PRON',
    'f5_PROPN', 'f5_PUNCT', 'f5_SCONJ', 'f5_SYM', 'f5_VERB',
    'f5_X', 'f6_ADJ', 'f6_ADP', 'f6_ADV', 'f6_AUX', 'f6_CCONJ',
    'f6_DET', 'f6_END', 'f6_NOUN', 'f6_NUM', 'f6_PRON',
    'f6_PROPN', 'f6_PUNCT', 'f6_SCONJ', 'f6_SYM', 'f6_VERB',
    'f6_X', 'f7_ADJ', 'f7_ADP', 'f7_ADV', 'f7_CCONJ', 'f7_DET',
    'f7_END', 'f7_NOUN', 'f7_NUM', 'f7_PRON', 'f7_PROPN',
    'f7_PUNCT', 'f7_SCONJ', 'f7_SYM', 'f7_VERB', 'f7_X'
]

def generate_features(doc, pos):
  len_doc = len(doc)
  features = []
  for i in [-3,-2,-1, 0,1,2,3]:
    feat_pos = pos + i
    if feat_pos < 0:
      features.append('START')
    elif feat_pos >= len_doc:
      features.append('END')
    else:
      features.append(doc[feat_pos].pos_)
  return features

def predict_entities(sent):
  d = pd.DataFrame(columns=columns[:-1])
  doc = nlp(sent)
  for i, _ in enumerate(doc):
    new_row = generate_features(doc, i)
    d = d.append(pd.DataFrame([new_row], columns=columns[:-1]))
  d = pd.get_dummies(d)
  # Get missing columns in the training test
  missing_cols = set( features_columns ) - set( d.columns )
  # Add a missing column in test set with default value equal to 0
  for c in missing_cols:
      d[c] = 0
  # Ensure the order of column in the test set is in the same order than in train set
  d = d[features_columns]
  return [{'word': str(w), 'entity': e} for (w, e) in list(zip(doc, [labels_encoder.inverse_transform(x) for x in entities_model.predict(d)]))]


