import nltk
import json
from pymongo import MongoClient
import trainandtest

def word2features(doc, i):
    word = doc[i][0]
    postag = doc[i][1]

    # Common features for all words
    features = [
        'bias',
        'word.lower=' + word.lower(),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
        'postag=' + postag
    ]

    # Features for words that are not
    # at the beginning of a document
    if i > 0:
        word1 = doc[i - 1][0]
        postag1 = doc[i - 1][1]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isupper=%s' % word1.isupper(),
            '-1:word.isdigit=%s' % word1.isdigit(),
            '-1:postag=' + postag1
        ])
    else:
        # Indicate that it is the 'beginning of a document'
        features.append('BOS')

    # Features for words that are not
    # at the end of a document
    if i < len(doc) - 1:
        word1 = doc[i + 1][0]
        postag1 = doc[i + 1][1]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isupper=%s' % word1.isupper(),
            '+1:word.isdigit=%s' % word1.isdigit(),
            '+1:postag=' + postag1
        ])
    else:
        # Indicate that it is the 'end of a document'
        features.append('EOS')

    return features


def extract_features(doc):
    return [word2features(doc, i) for i in range(len(doc))]

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.local
collection = db.Abatacept
docs =[]
text =[]
cursor = collection.find()
for new in cursor:

    text.append(new.get('ProcessedAbstract'))
docs.append(text)

data = []
for x in range(len(docs)):
    for tokens in docs[x]:
        for a in tokens:

            # Obtain the list of tokens in the document


            # Perform POS tagging
            b = nltk.word_tokenize(a)
            tagged = nltk.pos_tag(b)


    # Take the word, POS tag, and its label
            data.append(tagged)
print(data)
X = [extract_features(doc) for doc in data]

X_test= X

thefile = open('x_test1.txt', 'w')

json.dump(X_test, thefile)
thefile.close()

'''
def predict():

    for i in range(len(trainandtest.X_test1)):
        for x, y in zip(trainandtest.y_pred1[i], [x[1].split("=")[1] for x in trainandtest.X_test1[i]]):
            print((y, x))

predict()

'''