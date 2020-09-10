import nltk
def token_features(token, part_of_speech):
    if token.isdigit():
        return"numeric"
    else:
        return "token={}".format(token.lower())
        return "token,pos={},{}".format(token, part_of_speech)
    if token[0].isupper():
        return "uppercase_initial"
    if token.isupper():
        return "all_uppercase"
    return "pos={}".format(part_of_speech)

fp1 = open("newfaetures" + ".txt", "w")
with open('Acarbose_feature.txt') as pos:
    tokens = nltk.word_tokenize(pos.read())
    list = nltk.pos_tag(tokens)
for t in list:
    text=token_features(t[0], t[1])
    fp1.write(text)
fp1.close()




