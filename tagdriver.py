import nltk
from nltk.corpus import brown
from pickle import dump
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
import numpy as np
from sklearn.preprocessing import normalize
from collections import defaultdict
import sklearn_crfsuite

brown_tagged_sents = brown.tagged_sents()
def ngramTagger(train_sents, n=2, defaultTag='NN'):
    t0 = nltk.DefaultTagger(defaultTag)
    if (n <= 0):
        return t0
    elif (n == 1):
        t1 = nltk.UnigramTagger(train_sents, backoff=t0)
        return t1
    elif (n == 2):
        t1 = nltk.UnigramTagger(train_sents, backoff=t0)
        t2 = nltk.BigramTagger(train_sents, backoff=t1)
        return t2
    else:
        t1 = nltk.UnigramTagger(train_sents, backoff=t0)
        t2 = nltk.BigramTagger(train_sents, backoff=t1)
        t3 = nltk.TrigramTagger(train_sents, backoff=t2)
        return t3
brown_tagged_sents = brown.tagged_sents()
size = int(len(brown_tagged_sents) * 0.7)
tags = [tag for (word, tag) in brown.tagged_words()]
defaultTag = nltk.FreqDist(tags).max()

train_sents = brown_tagged_sents[:size]
test_sents = brown_tagged_sents[size:]
tagger = ngramTagger(train_sents, 2, defaultTag)
def features(sentence, index):
    currWord = sentence[index][0]
    if (index > 0):
        prevWord = sentence[index - 1][0]
    else:
        prevWord = '<START>'
    if (index < len(sentence)-1):
        nextWord = sentence[index + 1][0]
    else:
        nextWord = '<END>'
    return {
        'word': currWord,
        'is_first': index == 0,
        'is_last': index == len(sentence) - 1,
        'curr_is_title': currWord.istitle(),
        'prev_is_title': prevWord.istitle(),
        'next_is_title': nextWord.istitle(),
        'curr_is_lower': currWord.islower(),
        'prev_is_lower': prevWord.islower(),
        'next_is_lower': nextWord.islower(),
        'curr_is_upper': currWord.isupper(),
        'prev_is_upper': prevWord.isupper(),
        'next_is_upper': nextWord.isupper(),
        'curr_is_digit': currWord.isdigit(),
        'prev_is_digit': prevWord.isdigit(),
        'next_is_digit': nextWord.isdigit(),
        'curr_prefix-1': currWord[0],
        'curr_prefix-2': currWord[:2],
        'curr_prefix-3': currWord[:3],
        'curr_suffix-1': currWord[-1],
        'curr_suffix-2': currWord[-2:],
        'curr_suffix-3': currWord[-3:],
        'prev_prefix-1': prevWord[0],
        'prev_prefix-2': prevWord[:2],
        'prev_prefix-3': prevWord[:3],
        'prev_suffix-1': prevWord[-1],
        'prev_suffix-2': prevWord[-2:],
        'prev_suffix-3': prevWord[-3:],
        'next_prefix-1': nextWord[0],
        'next_prefix-2': nextWord[:2],
        'next_prefix-3': nextWord[:3],
        'next_suffix-1': nextWord[-1],
        'next_suffix-2': nextWord[-2:],
        'next_suffix-3': nextWord[-3:],
        'prev_word': prevWord,
        'next_word': nextWord,
    }
def transformDataset(sentences):
    wordFeatures = []
    wordLabels = []
    for sent in sentences:
        for index in range(len(sent)):
            wordFeatures.append(features(sent, index))
            wordLabels.append(sent[index][1])
    return wordFeatures, wordLabels

def trainNaiveBayes(trainFeatures, trainLabels):
    clf = make_pipeline(DictVectorizer(sparse=False), GaussianNB())
    scores = cross_val_score(clf, trainFeatures, trainLabels, cv=5)
    clf.fit(trainFeatures, trainLabels)
    return clf, scores.mean()
brown_tagged_sents = brown.tagged_sents(categories='news')
size = int(len(brown_tagged_sents) * 0.7)
tags = [tag for (word, tag) in brown.tagged_words()]
defaultTag = nltk.FreqDist(tags).max()
train_sents = brown_tagged_sents[:size]
test_sents = brown_tagged_sents[size:]
tagger = ngramTagger(train_sents, 2, defaultTag)

trainFeatures, trainLabels = transformDataset(train_sents)
testFeatures, testLabels = transformDataset(test_sents)
print(trainLabels)