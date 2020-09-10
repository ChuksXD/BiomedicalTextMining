import naivebayes
import xml.etree.ElementTree as ET
import nltk

tree = ET.parse('Alprazolam_ddi.xml')
root = tree.getroot()
docs = []
texts = []
with open('edited_testfile.txt') as f:
    words = f.read().split()


drugs = []
for elem in root:
    for subelem in elem.findall('entity'):
        drugs.append(subelem.get('text'))

for s in words:
    if s in drugs:

        label = "N"



    else:

        label = "I"

    for w in s.split(" "):
        if len(w)>0:
            texts.append((w, label))
docs.append(texts)
size = int(len(docs) * 0.7)

tags = [tag for (word, tag) in docs[0][:1]]
defaultTag = nltk.FreqDist(tags).max()

train_sents = docs[:size]
test_sents = docs[size:]

tagsDict = {}
for index, tag in enumerate(set(tags)):
    tagsDict[tag] = index

trainSeqFeatures, trainSeqLabels = naivebayes.transformDatasetSequence(train_sents)
testSeqFeatures, testSeqLabels = naivebayes.transformDatasetSequence(test_sents)

tagProbs, startProbs, transMat, emissionMat, featuresDict = naivebayes.trainHMM(trainSeqFeatures[:30000], trainSeqLabels[:30000], tagsDict)

predictedTags = naivebayes.predictTags(testSeqFeatures[:100], tagProbs, startProbs, transMat, emissionMat, tagsDict, featuresDict)
print(naivebayes.computeSeqAccuracy(predictedTags, [[tagsDict[tag] for tag in tags] for tags in testSeqLabels]))

tagger = naivebayes.ngramTagger(train_sents, 2, defaultTag)
print(tagger.evaluate(test_sents))

trainFeatures, trainLabels =naivebayes.transformDataset(train_sents)
testFeatures, testLabels = naivebayes.transformDataset(test_sents)

tree_model, tree_model_cv_score = naivebayes.trainDecisionTree(trainFeatures[:30000], trainLabels[:30000])
print(tree_model_cv_score)
print(tree_model.score(testFeatures, testLabels))

nb_model, nb_model_cv_score = naivebayes.trainNaiveBayes(trainFeatures[:30000], trainLabels[:30000])
print(nb_model_cv_score)
print(nb_model.score(testFeatures, testLabels))

nn_model, nn_model_cv_score = naivebayes.trainNN(trainFeatures[:30000], trainLabels[:30000])
print(nn_model_cv_score)
print(nn_model.score(testFeatures, testLabels))

crf_model = naivebayes.trainCRF(trainSeqFeatures[:30000], trainSeqLabels[:30000])
pred_labels = crf_model.predict(testSeqFeatures)
print(naivebayes.computeSeqAccuracy(pred_labels, testSeqLabels))