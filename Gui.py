from tkinter import *
import os
import time
from Bio import Entrez
from Bio import Medline
import testnaive
import trainandtest
class Placeholder_State(object):
    __slots__ = 'normal_color', 'normal_font', 'placeholder_text', 'placeholder_color', 'placeholder_font', 'with_placeholder'


def add_placeholder_to(entry, placeholder, color="grey", font=None):
    normal_color = entry.cget("fg")
    normal_font = entry.cget("font")

    if font is None:
        font = normal_font

    state = Placeholder_State()
    state.normal_color = normal_color
    state.normal_font = normal_font
    state.placeholder_color = color
    state.placeholder_font = font
    state.placeholder_text = placeholder
    state.with_placeholder = True

    def on_focusin(event, entry=entry, state=state):
        if state.with_placeholder:
            entry.delete(0, "end")
            entry.config(fg=state.normal_color, font=state.normal_font)

            state.with_placeholder = False

    def on_focusout(event, entry=entry, state=state):
        if entry.get() == '':
            entry.insert(0, state.placeholder_text)
            entry.config(fg=state.placeholder_color, font=state.placeholder_font)

            state.with_placeholder = True

    entry.insert(0, placeholder)
    entry.config(fg=color, font=font)

    entry.bind('<FocusIn>', on_focusin, add="+")
    entry.bind('<FocusOut>', on_focusout, add="+")

    entry.placeholder_state = state

    return state


class BioInterface:

    def __init__(self, master):
        self.master = master
        master.title("BioInterface Search")

        self.entered_string = ""
        self.entered_string2 = ""
        self.entered_string3 = ""

        self.temp = ""

        self.label = Label(master, text="Enter Keyword to Search")
        self.label2 = Label(master, text="Enter pubmed id")
        self.label3 = Label(master, text="enter batch number")
        self.label4 = Label(master, text="DRUG ENTITY EXTRACTION", fg="light green", bg="dark green",
                            font="Helevetica 16 bold italic")

        vcmd = master.register(self.validate)
        vcmd2 = master.register(self.validate2)
        vcmd3 = master.register(self.validate3)
        self.entry = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        add_placeholder_to(self.entry, 'Enter keyword eg drugs')
        self.entry2 = Entry(master, validate="key", validatecommand=(vcmd2, '%P'))
        self.entry3 = Entry(master, validate="key", validatecommand=(vcmd3, '%P'))

        self.count_button = Button(master, text="Count Articles", command=self.count_articles)
        self.download_button = Button(master, text="Download article PubMed ID", command=self.download_id)
        self.extract_button = Button(master, text="Extract Information", command=self.extract_info)
        self.save_file_button = Button(master, text="Download and save file", command=self.save_file)
        self.download_all_button = Button(master, text="Download all", command=self.save_all)
        self.use_crf = Button(master, text="test with crf", command=self.crf)
        self.use_naive = Button(master, text="test with naive bayes", command=self.naive)
        self.predict_drug =Button(master, text="Predict stored data", command= self.predict)

        # LAYOUT

        self.label.grid(row=1, column=0, sticky=W)
        self.label2.grid(row=5, column=0, sticky=W)

        self.label4.grid(row=0, column=0, columnspan=4, sticky=W + E)


        self.entry.grid(row=2, column=0, columnspan=3, sticky=W + E)
        self.entry2.grid(row=6, column=0, columnspan=3, sticky=W + E)
        self.entry3.grid(row=3, column=0, columnspan=3, sticky=W + E)

        self.count_button.grid(row=4, column=0)
        self.download_button.grid(row=4, column=1)
        self.extract_button.grid(row=7, column=0)
        self.save_file_button.grid(row=7, column=1)
        self.download_all_button.grid(row=7, column=2)
        self.use_crf.grid(row=11, column=0)
        self.use_naive.grid(row=8, column=0)
        self.predict_drug.grid(row=11, column=1)

        #for naive bayes
        self.S = Scrollbar(self.master)
        self.T = Text(self.master, height=6, width=50)
        self.S.grid(row=10, sticky=E)
        self.T.grid(row=10, sticky=W)
        self.S.config(command=self.T.yview)
        self.T.config(yscrollcommand=self.S.set)
        #for crf

        self.S1 = Scrollbar(self.master)
        self.T1 = Text(self.master, height=6, width=50)
        self.S1.grid(row=13, sticky=E,column=0)
        self.T1.grid(row=13, sticky=W,column=0)
        self.S1.config(command=self.T1.yview)
        self.T1.config(yscrollcommand=self.S1.set)

        #for predict

        self.S2 = Scrollbar(self.master)
        self.T2 = Text(self.master, height=6, width=50)
        self.S2.grid(row=13, sticky=E,column=1)
        self.T2.grid(row=13, sticky=W,column=1)
        self.S2.config(command=self.T2.yview)
        self.T2.config(yscrollcommand=self.S2.set)


    def validate(self, new_text):
        if not new_text:  # the field is being cleared
            self.entered_string = ""
            return True

        try:
            self.entered_string = new_text
            return True
        except ValueError:
            return False

    def validate2(self, new_text):
        if not new_text:  # the field is being cleared
            self.entered_string2 = ""
            return True

        try:
            self.entered_string2 = "\"" + new_text + "\""
            return True
        except ValueError:
            return False

    def validate3(self, new_text):
        if not new_text:  # the field is being cleared
            self.entered_string3 = ""
            return True

        try:
            self.entered_string3 = new_text
            return True
        except ValueError:
            return False

    def check(self):
        if self.entered_string3:
            self.temp = "\"" + self.entered_string + "\"" + " " + " AND " + " " + "\"" + self.entered_string3 + "\""

        else:
            self.temp = self.entered_string

    def count_articles(self):
        Entrez.email = "chuksxd@gmail.com"
        self.check()
        handle = Entrez.egquery(
            term=self.temp)
        record = Entrez.read(handle)

        for row in record["eGQueryResult"]:
            if row["DbName"] == "pubmed":
                print(row["Count"])

    def download_id(self):
        Entrez.email = "chuksxd@gmail.com"
        self.check()
        handle = Entrez.esearch(db="pubmed", term=self.temp, retmax=463)
        record = Entrez.read(handle)
        handle.close()
        idlist = record["IdList"]
        print(idlist)

    def extract_info(self):
        Entrez.email = "chuksxd@gmail.com"
        handle = Entrez.efetch(db="pubmed", id=self.entered_string2, rettype="medline", retmode="text")
        records = Medline.parse(handle)
        records = list(records)
        for record in records:
            print("title:", record.get("TI", "?"))
            print("authors:", record.get("AU", "?"))
            print("source:", record.get("SO", "?"))
            print("")

    def save_file(self):
        Entrez.email = "chuksxd@gmail.com"
        filename = self.entered_string2.strip('/"') + ".txt"
        if not os.path.isfile(filename):
            # Downloading...
            net_handle = Entrez.efetch(db="pubmed", id=self.entered_string2, rettype="medline", retmode="xml")
            out_handle = open(filename, "w")
            out_handle.write(net_handle.read())
            out_handle.close()
            net_handle.close()
            path = os.path.abspath(filename)
            directory = os.path.dirname(path)
            print("Saved in ", directory)

    def save_all(self):
        Entrez.email = "chuksxd@gmail.com"
        self.check()
        search_handle = Entrez.esearch(db="pubmed", term=self.temp,
                                       usehistory="y")
        search_results = Entrez.read(search_handle)
        search_handle.close()
        count = int(search_results["Count"])
        webenv = search_results["WebEnv"]
        query_key = search_results["QueryKey"]
        try:
            from urllib.error import HTTPError  # for Python 3
        except ImportError:
            from urllib.error import HTTPError

        batch_size = 3
        filename2 = self.temp.strip('/"') + ".txt"
        out_handle = open(filename2, "w")
        for start in range(0, count, batch_size):
            end = min(count, start + batch_size)
            print("Going to download record %i to %i" % (start + 1, end))
            attempt = 0
            while attempt < 3:
                attempt += 1
                try:
                    fetch_handle = Entrez.efetch(db="pubmed",
                                                 rettype="medline", retmode="text",
                                                 retstart=start, retmax=batch_size,
                                                 webenv=webenv, query_key=query_key,
                                                 )
                except HTTPError as err:
                    if 500 <= err.code <= 599:
                        print("Received error from server %s" % err)
                        print("Attempt %i of 3" % attempt)
                        time.sleep(15)
                    else:
                        raise
            data = fetch_handle.read()
            fetch_handle.close()
            out_handle.write(data)
        out_handle.close()
        path = os.path.abspath(filename2)
        directory = os.path.dirname(path)
        print("Saved in ", directory)
    def crf(self):
        x="crf model score=" + str(trainandtest.flat_accuracy_score(trainandtest.Y_test,trainandtest.y_pred))
        self.label6 = Label(self.master, text=x, fg="blue")
        self.label6.grid(row=12, column=0)
        for i in range(len(trainandtest.X_test)):
            for x, y in zip(trainandtest.y_pred[i], [x[1].split("=")[1] for x in trainandtest.X_test[i]]):
                z=str((y, x)) + "\n"

                self.T1.insert(END, z)


    def naive(self):

        y ="naive bayes model score =" + str(testnaive.nb_model.score(testnaive.testFeatures[:1000], testnaive.testLabels[:1000]))
        self.label5 = Label(self.master, text=y , fg="blue")
        self.label5.grid(row=9, column=0)
        for i in range(50):

            word1 = testnaive.testFeatures[i].get('word')

            for x in testnaive.y_pred[i]:
                z=str((word1, x)) + "\n"
                self.T.insert(END, z)
            for x in testnaive.group[i]:
                new_x =str(x) + "\n"
                self.T.insert(END, new_x)

    def predict(self):
        for i in range(len(trainandtest.X_test1)):
            for x, y in zip(trainandtest.y_pred1[i], [x[1].split("=")[1] for x in trainandtest.X_test1[i]]):
                z = str((y, x))  + "\n"
                self.T2.insert(END, z)


root = Tk()

my_gui = BioInterface(root)
root.mainloop()
