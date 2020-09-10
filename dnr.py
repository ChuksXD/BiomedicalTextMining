import xml.etree.ElementTree as ET

from bs4.element import Tag
import codecs
import nltk
import json

tree = ET.parse('combined_file.xml')
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

        label = "Drug"



    else:

        label = "NonDrug"

    for w in s.split(" "):
        if len(w)>0:
            texts.append((w, label))
docs.append(texts)


data = []
for i, doc in enumerate(docs):
    # Obtain the list of tokens in the document
    tokens = [t for t, label in doc]

    # Perform POS tagging
    tagged = nltk.pos_tag(tokens)

    # Take the word, POS tag, and its label
    data.append([(w, pos, label) for (w, label), (word, pos) in zip(doc, tagged)])

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


# A function for extracting features in documents
def extract_features(doc):
    return [word2features(doc, i) for i in range(len(doc))]


# A function fo generating the list of labels for each document
def get_labels(doc):
    return [label for (token, postag, label) in doc]


X = [extract_features(doc) for doc in data]
y = [get_labels(doc) for doc in data]


train = int(0.9*len(y[0]))
X_train= [X[0][:train]]
X_test=[X[0][train:]]
y_train=[y[0][:train]]

y_test =[y[0][train:]]

thefile = open('x_test.txt', 'w')

json.dump(X_test, thefile)
thefile.close()


thefile1 = open('x_train.txt', 'w')

json.dump(X_train, thefile1)
thefile1.close()

thefile2 = open('y_train.txt', 'w')

json.dump(y_train, thefile2)
thefile2.close()

thefile3 = open('y_test.txt', 'w')

json.dump(y_test, thefile3)
thefile3.close()
