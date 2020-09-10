import numpy as np
from sklearn.model_selection import train_test_split
from bs4.element import Tag
import codecs
import nltk
import json
import itertools
import re
import xml.etree.ElementTree as ET

tree = ET.parse('Acarbose_ddi.xml')
root = tree.getroot()
drugs = []
sentence = []
texts = []
docs = []

for elem in root:
    for subelem in elem.findall('entity'):
        drugs.append(subelem.get('text'))
for elem in root:
    sentence.append(elem.get('text'))

'''
def compare(list1, list2):
    for x in list1:
        if x in list2:
            label = "N"
        else:
            label = "I"
        for w in list1:
            if len(w) > 0:
                texts.append((w, label))
    docs.append(texts)
'''



b = np.array(sentence)
sentence1 = b.ravel()


for d in sentence1:
    if d in drugs:

        label = "N"


    for w in d.split():
        if len(w) > 0:
            texts.append((w, label))
docs.append(texts)

#compare( sentence, drugs)

for x in range(len(docs)):
    for y in range(len(docs[x])):
        print(docs[x][y])
