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

os.chdir('C:/Users/vishnu.sk/Desktop')
count_vect = CountVectorizer()
tfidf_transformer = TfidfTransformer()

if __name__ == '__main__':
    data_frame = pd.read_csv('bot_training.csv')
    data_frame['User_Queries'] = data_frame['User_Queries'].astype(str)
    X_train_counts = count_vect.fit_transform(data_frame['User_Queries'])
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    text_clf = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()),
                         ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                               alpha=1e-3, n_iter=5, random_state=42)), ])
    new_doc = [' i need a home in miami', 'help me to sell my house in miami', 'give me the best properties in miami', 'suggest me good properties in my neighbourhood', 'do you like pets?']
    text_clf.fit(data_frame['User_Queries'], data_frame['Label'])
    predicted = text_clf.predict(new_doc)
    print (predicted)
    joblib.dump(text_clf, 'model_top.pkl')
