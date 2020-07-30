import os
import sys
import numpy as np
import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Get path of topic and doc files
basepath = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(basepath, "dataset")
vector_path = os.path.join(basepath, "dataset_vector")
if not os.path.exists(vector_path):
    os.mkdir(vector_path)

def remove_between(document, start_str, end_str):

    while start_str in document and end_str in document:
        # Get start and end index
        start_str_index = document.find(start_str)
        end_str_index = document.find(end_str, start_str_index) + len(end_str) - 1
        # get new content without from start to end
        document = document[0: start_str_index] + document[end_str_index + 1: len(document)]
    return document

# Compute TF
def computeTF(wordDict, bagOfWords):
    tfDict = {}
    bagOfWordsCount = len(bagOfWords)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict

# Compute IDF
def computeIDF(documents):
    import math
    N = len(documents)
    idfDict = dict.fromkeys(documents[0].keys(), 0)
    for document in documents:
        for word, val in document.items():
            if val > 0:
                idfDict[word] += 1

    for word, val in idfDict.items():
        idfDict[word] = math.log(N / float(val))
    return idfDict

# Compute IFIDF
def computeTFIDF(tfBagOfWords, idfs):
    tfidf = {}
    for word, val in tfBagOfWords.items():
        tfidf[word] = val * idfs[word]
    return tfidf

def main():

    topics = next(os.walk(dataset_path))[1]
    throw_str =["is","be","the","will","a","of","to","and","or","in","are","The","with","we","me","as","As","that","it","these","he","his","him","by","such","for","which","after","have"]
    for topic in topics :
        # Get several paths for txt file
        topic_dir = os.path.join(dataset_path,topic)
        dir = os.path.join(vector_path,topic)
        if not os.path.exists(dir):
            os.mkdir(dir)
        subfiles = next(os.walk(topic_dir))[2]
        texts = []
        newfiles = []
        realwordlist = []
        tfidf_files = []
        newfile = ""
        boolean_path = os.path.join(dir,"boolean")
        tfidf_path = os.path.join(dir, "tfidf")
        for subfile in subfiles:
            filename = os.path.join(topic_dir,subfile)
            newfile = os.path.join(boolean_path,subfile)
            tfidf_file = os.path.join(tfidf_path,subfile)
            newfiles.append(newfile)
            tfidf_files.append(tfidf_file)
            fileContent = ""
            # Read txt file in dataset
            with open(filename,"r",encoding="utf-8") as file:
                fileContent = file.read()
            if "\t" in fileContent:
                fileContent = str(fileContent).replace("\t","")
            # Get filecontent as word
            fileContent = str(fileContent).split(" ")
            realword = []
            k = 0
            # Remove part in word that dont need
            for word in fileContent:
                word = remove_between(word, "[", "]").strip(" ")
                if "" == word or "." in str(word) or ":" in str(word) or "," in str(word) or "\\" in str(word) or "&" in str(word) or "#" in str(word) or "(" in str(word) or ")" in str(word) or "-" in str(word) or "'" in str(word) or '"' in str(word) or "th" in str(word):
                    continue
                elif word in "1234567890":
                    continue
                elif word in throw_str:
                    continue
                elif word.isnumeric():
                    continue
                elif not word in texts:
                    texts.append(word)
                realword.append(word)
                k = k + 1
                if k > 300:
                    break
            realwordlist.append(realword)
            file.close()
        mapping = {}
        for x in range(len(texts)):
            mapping[texts[x]] = x
        one_hot_encode = []
        numOfWordslist = []
        tfbag = []
        # Check folder exist
        if not os.path.exists(boolean_path):
            os.mkdir(boolean_path)
        for i in range(len(realwordlist)):
            encoded = []
            one_hot_encode = [0] * len(texts)
            numOfWords = dict.fromkeys(texts, 0)
            # Compute for each word
            for word in realwordlist[i]:
                numOfWords[word] += 1
                arr = list(np.zeros(len(texts), dtype=int))
                arr[mapping[word]] = 1
                one_hot_encode.append(arr)
                each_line = ""
                for each_char in arr:
                    each_line = each_line + str(each_char) + " "
                for arr_index in range(len(texts)):
                    one_hot_encode[arr_index] = one_hot_encode[arr_index] + int(arr[arr_index])
                encoded.append(each_line)
            numOfWordslist.append(numOfWords)
            tf = computeTF(numOfWords, realwordlist[i])
            tfbag.append(tf)
            with open(newfiles[i], "w") as file:
                for line in encoded:
                    file.write(line)
                    file.write("\n")
                file.write(str(one_hot_encode))
            file.close()
        if not os.path.exists(tfidf_path):
            os.mkdir(tfidf_path)
        idfs = computeIDF(numOfWordslist)
        tfidfs = []
        for i in range(len(tfidf_files)):
            tfidf = computeTFIDF(tfbag[i],idfs)
            with open(tfidf_files[i], "w",encoding="utf-8") as file:
                for line in tfidf:
                    file.write(str(line) + ":" + str(tfidf[line]))
                    file.write("\n")
            file.close()
            tfidfs.append(tfidf)
        df = pd.DataFrame(tfidfs)
main()


