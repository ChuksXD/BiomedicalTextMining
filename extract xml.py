from xml.dom import minidom

xmldoc = minidom.parse('Alprazolam_ddi.xml')
filename = "testfile"
itemlist = xmldoc.getElementsByTagName('sentence')
fp1 = open(filename + ".txt", "w")
for s in itemlist:
    text = s.attributes['text'].value + '\n'
    fp1.write(text)

fp1.close()