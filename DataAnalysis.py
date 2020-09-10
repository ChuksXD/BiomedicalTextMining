import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from pymongo import MongoClient


def process(words, Id):
    new_word = re.sub("'AbstractText':", " ", str(words))
    letters_only = re.sub("[^a-zA-Z]", " ", str(new_word))
    word_token = word_tokenize(letters_only)
    stop_words = set(stopwords.words('english'))
    filtered_sentence = []
    for w in word_token:
        if w not in stop_words:
            filtered_sentence.append(w)

    collection.update({'_id': Id}, {'$set': {"ProcessedAbstract": filtered_sentence}}, False, True)


client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.local
collection = db.Bio

cursor = collection.find()

for new in cursor:
    ar = new.get('_id')
    words1 = new.get('AbstractText')
    process(words1, ar)
