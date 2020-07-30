import os
import sys

# Execute the following script to import the required libraries:
import numpy as np
import re
from sklearn.datasets import load_files
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stemmer = WordNetLemmatizer()
# package for load
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Get path of topic and doc files
basepath = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(basepath, "dataset")

def remove_between(document, start_str, end_str):

    while start_str in document and end_str in document:
        # Get start and end index
        start_str_index = document.find(start_str)
        end_str_index = document.find(end_str, start_str_index) + len(end_str) - 1
        # get new content without from start to end
        document = document[0: start_str_index] + document[end_str_index + 1: len(document)]
    return document

def main():

    documents = []
    # Load files in dataset
    txt_data = load_files(dataset_path)
    X, y = txt_data.data, txt_data.target
    # text processing for get good conditoin word
    for sen in range(0, len(X)):
        document = re.sub(r'\W', ' ', str(X[sen]))
        # remove all single characters
        document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
        # Remove single characters from the start
        document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)
        document = ''.join([i for i in document if not i.isdigit()])
        # Substituting multiple spaces with single space
        document = re.sub(r'\s+', ' ', document, flags=re.I)
        # Removing prefixed 'b'
        document = re.sub(r'^b\s+', '', document)
        # Converting to Lowercase
        document = document.lower()
        documents.append(document)
    # bag of words model to convert text documents into corresponding numerical features
    vectorizer = CountVectorizer(max_features=3000, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
    X = vectorizer.fit_transform(documents).toarray()
    # convert values obtained using the bag of words model into TFIDFvalues
    tfidfconverter = TfidfTransformer()
    X = tfidfconverter.fit_transform(X).toarray()
    # Training and Testing Sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=0)
    # Training Text Classification Model and Predicting Sentiment
    classifier = RandomForestClassifier(n_estimators=1000, random_state=0)
    classifier.fit(X_train, y_train)
    # predict the sentiment for the documents in test set
    y_pred = classifier.predict(X_test)
    # print(confusion_matrix(y_test, y_pred))
    # print(classification_report(y_test, y_pred))
    # print(accuracy_score(y_test, y_pred))
    with open('text_classifier', 'wb') as picklefile:
        pickle.dump(classifier, picklefile)
    # load model for check
    with open('text_classifier', 'rb') as training_model:
        model = pickle.load(training_model)
    # Check model with exist documents
    y_pred2 = model.predict(X_test)
    print(confusion_matrix(y_test, y_pred2))
    print(classification_report(y_test, y_pred2))
    print(accuracy_score(y_test, y_pred2))
    # Write report for check
    with open('report.txt', 'w') as file:
        file.write(str(confusion_matrix(y_test, y_pred2)))
        file.write(str(classification_report(y_test, y_pred2)))
        file.write(str(accuracy_score(y_test, y_pred2)))

main()



