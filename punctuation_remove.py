import string

def remove(a):
    # to remove the punctuations from a string


    # make a set of all possible punctuation marks
    punctuation_replacer = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    # make a string which does not hv punctuation marks
    sans_punct = ' '.join(a.translate(punctuation_replacer).split()).strip()
    return sans_punct

with open('testfile.txt') as f:
    words = f.read()
new_words = remove(words)
fp1 = open("edited_testfile"+ ".txt", "w")
for x in new_words:
    fp1.write(x)
fp1.close()