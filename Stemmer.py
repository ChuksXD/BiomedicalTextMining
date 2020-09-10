import nltk
from nltk.stem import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.stem import SnowballStemmer


def obtain_tokens():
    with open('Acarbose_feature.txt') as stem:
        tokens = nltk.word_tokenize(stem.read())
        return tokens


def stemming(filtered):
    stem = []
    for x in filtered:
        stem.append(PorterStemmer().stem(x))
    return stem


fp1 = open("newfeature" + ".txt", "w")
tok = obtain_tokens()
stem_tokens = stemming(tok)
for s in stem_tokens:
    text = s
    fp1.write(text)
fp1.close()
