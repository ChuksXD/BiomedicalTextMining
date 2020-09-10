# BiomedicalTextMining
Text Mining Framework that recognizes various biomedical entities when connected to a database like PubMed or DrugBank using Machine learning algorithms such as CRF and naive Bayes.
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Application GUI](#application-gui)
* [Setup](#Setup)

## General Info
Interactive biomedical text mining framework built with python to access the scientific abstracts online, to pre-process and to extract drug entity through state of art machine learning techniques such as CRF and naive bayes. 
This framework facilitates recognizing new drug names from real time biomedical abstracts from PubMed as well as from existing benchmark test datasets such as the DDI2013 Corpus. 
This project was built for the chemistry department, Karunya Institute of Technology and Sciences to facilitate their quick reseeach into newer drugs for cancer by scouring medical databases and extracting new drug names relating to cancer alleviation.

The GUI was built with python's tkinter package and data for training and testing the machine learning algorithms were obtained from PubMed's API.

## Application GUI

<img src="/images/tkinter1.png" alt="Profit by Algorithm" width="70%" height="70%">
<hr>

<img src="/images/tkinter2.png" alt="Profit vs Time block mined" width="70%" height="70%">

## Technologies
* Python
* Tkinter
* scikit-learn

## Setup
Clone the repository and execute the Gui.py file to lauch the application. Make sure you install the dependencies such as tkinter & 
scikit-learn. You will also need an internet connection to access the biomedical databases like PubMed through the GUI.

To compare the Naive bayes and CRF algorithms, run their individual file separately.
