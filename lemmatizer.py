import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
print(lemmatizer.lemmatize('believes'))
print(lemmatizer.lemmatize('cooking', pos='v'))