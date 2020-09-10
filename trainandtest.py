import pycrfsuite
import json
import numpy as np
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite.metrics import flat_accuracy_score
from sklearn.metrics import classification_report
trainer = pycrfsuite.Trainer(verbose=False)
train1= open('x_train.txt','r')
X_train= json.load(train1)

test1= open('x_test.txt','r')
X_test = json.load(test1)
test3 = open('x_test1.txt', 'r')
X_test1 = json.load(test3)
train2=open('y_train.txt','r')
y_train = json.load(train2)

test2=open('y_test.txt','r')
Y_test = json.load(test2)
# Submit training data to the trainer
for xseq, yseq in zip(X_train, y_train):
    trainer.append(xseq, yseq)

# Set the parameters of the model
trainer.set_params({
    # coefficient for L1 penalty
    'c1': 0.1,

    # coefficient for L2 penalty
    'c2': 0.01,

    # maximum number of iterations
    'max_iterations': 200,

    # whether to include transitions that
    # are possible, but not observed
    'feature.possible_transitions': True
})

# Provide a file name as a parameter to the train function, such that
# the model will be saved to the file when training is finished
trainer.train('crf.model')
tagger = pycrfsuite.Tagger()
tagger.open('crf.model')
y_pred = [tagger.tag(xseq) for xseq in X_test]
y_pred1 = [tagger.tag(xseq) for xseq in X_test1]
#print(flat_accuracy_score(Y_test,y_pred))

'''
# Let's take a look at a random sample in the testing set
for i in range(len(X_test)):
    for x, y in zip(y_pred[i], [x[1].split("=")[1] for x in X_test[i]]):
        print("%s (%s)" % (y, x))
'''
# Create a mapping of labels to indices
labels = {"NonDrug": 1, "Drug": 0}

# Convert the sequences of tags into a 1-dimensional array
predictions = np.array([labels[tag] for row in y_pred for tag in row])
truths = np.array([labels[tag] for row in Y_test for tag in row])
print(flat_accuracy_score(Y_test,y_pred))


# Print out the classification report
print(classification_report(
    truths, predictions,
    target_names=["NonDrug", "Drug"]))
