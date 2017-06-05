'''
Created on Feb 23, 2017

@author: vishnu.sk
'''

import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib

os.chdir('C:/Users/vishnu.sk/Documents/Chatbot')
count_vect = CountVectorizer()
tfidf_transformer = TfidfTransformer()

if __name__ == '__main__':
    data_frame = pd.read_csv('train_data.csv')
    data_frame['User_input'] = data_frame['User_input'].astype(str)
    X_train_counts = count_vect.fit_transform(data_frame['User_input'])
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    text_clf = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()),
                         ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                               alpha=1e-3, n_iter=5, random_state=42)), ])
    new_doc = ['I am looking for a house in trivandrum', 'I want a condo', 'i need 20 bed room house', '5k sqft', 'price not a problem']
    text_clf.fit(data_frame['User_input'], data_frame['Label'])
    predicted = text_clf.predict(new_doc)
    joblib.dump(text_clf, 'model.pkl')
