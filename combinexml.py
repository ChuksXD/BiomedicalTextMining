from xml.etree import ElementTree as et
import os
import sys
from xml.etree import ElementTree

def run(files):
    first = None
    for filename in files:
        data = ElementTree.parse(filename).getroot()
        if first is None:
            first = data
        else:
            first.extend(data)
    if first is not None:
        print(ElementTree.tostring(first))

if __name__ == "__main__":
    run(sys.argv[1:])

filename = "combine"

fp1 = open(filename + ".txt", "a")

path = "C:/Users/Chuks/Downloads/Compressed/APIforDDICorpus2013/APIforDDICorpus/DDICorpus/Train/DrugBank"

files =os.listdir(path)


r = run(files)
fp1.write(r)
'''
for filename in os.listdir(path):
    if not filename.endswith('.xml'): continue
    fullname = os.path.join(path, filename)
    #tree = et.parse(fullname)
    r = XMLCombiner((fullname)).combine()
    fp1.write(r)
'''
fp1.close()