import xml.etree.ElementTree as ET

import nltk, math, sys
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
import numpy as np
from sklearn.preprocessing import normalize
from collections import defaultdict
import sklearn_crfsuite


tree = ET.parse('combined_file.xml')
root = tree.getroot()
docs = []

with open('edited_testfile.txt') as f:
    words = f.read().split()
list =[]
with open('edited_testfile.txt') as pos:
    tokens = nltk.word_tokenize(pos.read())
    list = nltk.pos_tag(tokens)
drugs = []
for elem in root:
    for subelem in elem.findall('entity'):
        drugs.append(subelem.get('text'))

for s in words:
    if s in drugs:

        label = "Drug"



    else:

        label = "NonDrug"

    for w in s.split(" "):
        if len(w)>0:
            docs.append((w, label))


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
        #'is_first': index == 0,
        #'is_last': index == len(sentence) - 1,
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
def transformDatasetSequence(sentences):
    wordFeatures, wordLabels = [], []

    for sent in sentences:
        feats, labels = [], []

        for index in range(len(sent)):
            feats.append(features(sent, index))
            labels.append(sent[index][1])

        wordFeatures.append(feats)
        wordLabels.append(labels)

    return wordFeatures, wordLabels

def trainNaiveBayes(trainFeatures, trainLabels):
    clf = make_pipeline(DictVectorizer(sparse=False), GaussianNB())
    scores = cross_val_score(clf, trainFeatures, trainLabels, cv=2)
    clf.fit(trainFeatures, trainLabels)
    return clf, scores.mean()




size = int(0.7*len(docs))
tags = [tag for (word, tag) in list]
defaultTag = nltk.FreqDist(tags).max()
train_sents = docs[:size]
test_sents = docs[size:]



trainFeatures, trainLabels = transformDataset([train_sents])
testFeatures, testLabels = transformDataset([test_sents])


'''
length = len(trainFeatures)
length1 = len(trainLabels)
'''

nb_model, nb_model_cv_score = trainNaiveBayes(trainFeatures[:3000], trainLabels[:3000])
print(nb_model_cv_score)
print(nb_model.score(testFeatures[:3000], testLabels[:3000]))

y_pred = [nb_model.predict(xseq) for xseq in testFeatures]
#pred_tags = nb_model.predict(testFeatures[:3000])
group= [nb_model.predict_log_proba(aseq) for aseq in testFeatures]
#print predicted tags and already existing tags for comparison
'''
print(pred_tags)
print(testLabels)
'''


#test for a single value

def test():
    for i in range(50):

        word1 = testFeatures[i].get('word')


        for x in y_pred[i]:

            print("%s (%s)" % (word1, x))
        for x in group[i]:
            print(x)

test()

'''
def computeTagProbs(trainLabels, tagsDict):
    numTags = len(tagsDict)
    tagProbs = np.zeros(numTags)
    for sentenceLabels in trainLabels:
        for tag in sentenceLabels:
            tagProbs[tagsDict[tag]] += 1
    tagProbs += 1
    return tagProbs / np.sum(tagProbs)
def computeStartProbs(trainLabels, tagsDict):
    numTags = len(tagsDict)
    startProbs = np.zeros(numTags)
    for sentenceLabels in trainLabels:
        startTag = sentenceLabels[0]
        startProbs[tagsDict[startTag]] += 1
    startProbs += 1
    return startProbs/np.sum(startProbs)
def computeTransitionProbabilities(trainLabels, tagsDict):
    numTags = len(tagsDict)
    transMat = np.zeros(shape=(numTags, numTags))
    for sentenceLabels in trainLabels:
        for i in range(len(sentenceLabels)-1):
            tag1 = tagsDict[sentenceLabels[i]]
            tag2 = tagsDict[sentenceLabels[i+1]]
            transMat[tag1, tag2] += 1
    normalized_transmat = normalize(transMat+1, axis=1, norm='l1')
    return normalized_transmat
def computeEmissionProbabilities(trainFeatures, trainLabels, tagsDict):
    numTags = len(tagsDict)
    emissionDict = defaultdict(lambda: defaultdict(int))
    uniqueKeys = set()
    for i in range(len(trainLabels)):
        sentenceFeatures = trainFeatures[i]
        sentenceLabels = trainLabels[i]
        for j in range(len(sentenceLabels)):
            tag = sentenceLabels[j]
            for key, val in sentenceFeatures[j].iteritems():
                transformedKey = str(key) + "__" + str(val)
                uniqueKeys.add(transformedKey)
                emissionDict[tag][transformedKey] += 1
    emissionMat = np.zeros(shape=(numTags, len(uniqueKeys)))
    featuresDict = {}
    for index, key in enumerate(uniqueKeys):
        featuresDict[key] = index
    for tag in tagsDict.keys():
        for key in featuresDict.keys():
            i = tagsDict[tag]
            j = featuresDict[key]
            emissionMat[i, j] = emissionDict[tag][key]
    normalized_emissionMat = normalize(emissionMat+1, axis=1, norm='l1')
    return normalized_emissionMat, featuresDict

def predictTags(testFeatures, tagProbs, startProbs, transMat, emissionMat, tagsDict, featuresDict):
    numTags = len(tagsDict)
    bestTags = []
    for sentenceFeatures in testFeatures:
        bestTagsSentence = []
        lenSentence = len(sentenceFeatures)
        probMatrix, tagMatrix = np.zeros(shape=(lenSentence, numTags)), np.zeros(shape=(lenSentence, numTags))
        for index in range(lenSentence):
            feat = sentenceFeatures[index]
            for curr in range(numTags):
                emissionProb = 0
                for key, val in feat.iteritems():
                    transformedKey = str(key) + "__" + str(val)
                    if transformedKey in featuresDict:
                        emissionProb += math.log(emissionMat[curr, featuresDict[transformedKey]])
                    else:
                        emissionProb -= math.log(len(featuresDict))
                emissionProb += math.log(tagProbs[curr])
                maxProb = -sys.float_info.max
                maxProbTag = -1
                if index == 0:
                    probMatrix[index][curr] = math.log(startProbs[curr]) + emissionProb
                    tagMatrix[index][curr] = -1
                else:
                    for prev in range(numTags):
                        tagProb = math.log(transMat[prev, curr]) + math.log(probMatrix[index - 1][prev])
                        if (tagProb > maxProb):
                            maxProb = tagProb
                            maxProbTag = prev
                    maxProb += emissionProb
                    probMatrix[index][curr] = maxProb
                    tagMatrix[index][curr] = maxProbTag
            const = -np.mean(probMatrix[index])
            func = np.vectorize(lambda t: math.exp(t+const))
            probMatrix[index] = func(probMatrix[index])
            probMatrix = normalize(probMatrix, axis=1, norm='l1')
        prevBestTag = None
        for index in reversed(range(lenSentence+1)):
            if index == lenSentence:
                bestTag = probMatrix[index-1].argmax()
            else:
                bestTag = tagMatrix[index][prevBestTag]
            prevBestTag = int(bestTag)
            bestTagsSentence.append(prevBestTag)
        bestTags.append(list(reversed(bestTagsSentence))[1:])
    return bestTags

def transformDatasetSequence(sentences):
    wordFeatures, wordLabels = [], []
    for sent in sentences:
        feats, labels = [], []
        for index in range(len(sent)):
            feats.append(features(sent, index))
            labels.append(sent[index][1])
        wordFeatures.append(feats)
        wordLabels.append(labels)
    return wordFeatures, wordLabels

def trainHMM(trainFeatures, trainLabels, tagsDict):
    tagProbs = computeTagProbs(trainLabels, tagsDict)
    startProbs = computeStartProbs(trainLabels, tagsDict)
    transMat = computeTransitionProbabilities(trainLabels, tagsDict)
    emissionMat, featuresDict = computeEmissionProbabilities(trainFeatures, trainLabels, tagsDict)
    return tagProbs, startProbs, transMat, emissionMat, featuresDict
tagsDict = {}
for index, tag in enumerate(set(tags)):
    tagsDict[tag] = index
trainSeqFeatures, trainSeqLabels = transformDatasetSequence([train_sents])
testSeqFeatures, testSeqLabels = transformDatasetSequence([test_sents])



def trainCRF(trainFeatures, trainLabels):
    crf = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True,
    )
    crf.fit(trainFeatures, trainLabels)
    return crf

crf_model = trainCRF(trainSeqFeatures[:30000], trainSeqLabels[:30000])

pred_labels = crf_model.predict(testSeqFeatures)
'''''