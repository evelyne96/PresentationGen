
#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
import re, os, time, string


import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import SnowballStemmer

datasetPath = '../../dataset3/1_paperXMLs/'
stemmer = SnowballStemmer("english")

stop_words = set(stopwords.words('english')) 
stop_words.update(['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm'])
stop_words = [stemmer.stem(w) for w in stop_words]
stop_words += ["'d", 'might', "n't", 'need', 'sha', 'wo', 'would', 'could', 'must']

def filterStopWords(word):
    if (word in stop_words) or len(word) == 1 or word.isdigit():
        return True
    else:
        return False 

#-----------------------------------------Read data + Preprocessing--------------------------------------------------------------------

# Grobid documentation (Install/build/Run): https://grobid.readthedocs.io/en/latest/
# Grobid python client github: https://github.com/kermitt2/grobid-client-python

# <div> </div> - Section
# <heade> </head> - Section title
class Section:
    def __init__(self, secTitle: str, paragraphs: List[str]):
        self.secTitle = secTitle
        if secTitle != None:
            self.secTitle_stem_tokenized = [stemmer.stem(w) for w in word_tokenize(secTitle.translate(str.maketrans(' ',' ', string.punctuation)))]
            self.text = self.secTitle
        else:
            self.secTitle_stem_tokenized = []
            self.text = "The"

    
        self.paragraphs = paragraphs

        self.sec_sent_tokenized = []
        for p in paragraphs:
          self.sec_sent_tokenized = self.sec_sent_tokenized + sent_tokenize(p)
        
        self.sec_sent_tokenized = [s.translate(str.maketrans(' ',' ', string.punctuation))  for s in self.sec_sent_tokenized if len(s) > 4]
        self.sec_sent_word_tokenized = []
        self.sec_sent_stem_tokenized = []
        
        for sent in self.sec_sent_tokenized:
            self.sec_sent_word_tokenized.append(word_tokenize(sent))
            self.sec_sent_stem_tokenized.append([stemmer.stem(w) for w in self.sec_sent_word_tokenized[-1]])
            self.text = self.text + " " + sent

class TeiText:
    def __init__(self, id: str, title: str, sections: List[Section], author: str):
        self.sections = sections
        self.id = id
        self.author = author
        self.title = title
        if title != None:
            self.title_stem_tokenized =  [stemmer.stem(w) for w in word_tokenize(title.translate(str.maketrans(' ',' ', string.punctuation)))]
            self.text = self.title
            self.titles = " ".join(self.title_stem_tokenized)
        else:
            self.title_stem_tokenized = []
            self.text = ""
            self.titles = " "

        # self.text_word_tokenized = self.title_stem_tokenized
        
        for s in sections:
            if s.secTitle != None:
                self.titles = self.titles + " " + " ".join(s.secTitle_stem_tokenized)
            
            self.text = self.text + " " + s.text.replace('. . .', ' ').replace('· · ·', ' ')

            # for sent in s.sec_sent_stem_tokenized:
            #     self.text_word_tokenized += sent
    
    def getSentences(self, indices):
        nr = 0
        i = 0 
        sentences = []
        for s in self.sections:
            nrOfSent = len(s.sec_sent_tokenized)
            while (i < len(indices) and indices[i] - nr < nrOfSent):
                sentences.append(s.sec_sent_tokenized[indices[i]-nr])
                i = i + 1
            
            nr = nr + nrOfSent
        
        return sentences


#root
#{'{http://www.w3.org/XML/1998/namespace}lang': 'en'} {http://www.tei-c.org/ns/1.0}teiHeader
#{'{http://www.w3.org/XML/1998/namespace}lang': 'en'} {http://www.tei-c.org/ns/1.0}text
class GrobidXMLParser:
    def __init__(self):
        self.xmlns = '{http://www.tei-c.org/ns/1.0}'


    def createId(self, name):
        return self.xmlns + name

    def getTitle(self, root):
        title = root.find(self.createId('teiHeader')).find(self.createId('fileDesc')).find(self.createId('titleStmt')).find(self.createId('title')).text
        if title != None:
            title = title.lower()
        return title

    def getAuthor(self, root):
        pers = root.find(self.createId('teiHeader')).find(self.createId('fileDesc')).find(self.createId('sourceDesc')).find(self.createId('biblStruct')).find(self.createId('analytic')).find(self.createId('author')).find(self.createId('persName'))
        forename = pers.find(self.createId('forename')).text
        surname = pers.find(self.createId('surname')).text

        return forename + " " + surname

    def getSections(self, root):
        body = root.find(self.createId('text')).find(self.createId('body'))
        sectionList = []
        sections = body.findall(self.createId('div'))
        if len(sections) > 0:
            for sec in sections:
                sectionTitle = sec.find(self.createId('head'))
                if sectionTitle != None:
                    sectionTitle = sectionTitle.text.lower()
                
                paragraphs = [p.text.lower() for p in sec.findall(self.createId('p'))]
                
                sectionList.append(Section(sectionTitle, paragraphs))

        
        return sectionList

def readData():
    xmlHelper = GrobidXMLParser()
    papers = []
    persentations = []
    lastPaper = None
    lastPres = None

    for x in os.listdir(datasetPath):
        fullPath = datasetPath+x
        # print(fullPath)
        
        if os.path.isfile(fullPath):
            tree = ET.parse(fullPath)
            root = tree.getroot()

            title = xmlHelper.getTitle(root)
            sections = xmlHelper.getSections(root)
            author = xmlHelper.getAuthor(root)

            if len(sections) > 0:
                if 'paper' in x:
                    lastPaper = TeiText(x, title, sections, author) 
                else:
                    lastPres = TeiText(x, title, sections, "")
            
            if lastPaper != None and lastPres != None:
                papers.append(lastPaper)
                persentations.append(lastPres)
                lastPaper = None
                lastPres = None

    return (papers, persentations)

def readPData(paper_name):
    xmlHelper = GrobidXMLParser()
    fullPath = datasetPath + paper_name
    paper = None

    if os.path.isfile(fullPath):
        # print('FILE')
        tree = ET.parse(fullPath)
        root = tree.getroot()
        # print(fullPath)
        title = xmlHelper.getTitle(root)
        sections = xmlHelper.getSections(root)
        author = xmlHelper.getAuthor(root)

        paper = TeiText(paper_name, title, sections, author)

    return paper


def readData2():
    xmlHelper = GrobidXMLParser()
    papers = []
    persentations = []
    lastPaper = None
    lastPres = None

    papers_path = '../../dataset3/1_paperXMLs/'
    pres_path = '../../dataset3/presXMLs/'

    for x in os.listdir(papers_path):
        paper_fullPath = papers_path + x
        pres_fullPath = pres_path + x.split('paper')[0]+'pres.xml'
        
        if os.path.isfile(paper_fullPath) and os.path.isfile(pres_fullPath):
            tree = ET.parse(paper_fullPath)
            root = tree.getroot()

            title = xmlHelper.getTitle(root)
            author = xmlHelper.getAuthor(root)
            sections = xmlHelper.getSections(root)

            if len(sections) > 0:
                lastPaper = TeiText(x, title, sections, author)

            # print(pres_fullPath)
            tree = ET.parse(pres_fullPath)
            root = tree.getroot()

            title = xmlHelper.getTitle(root)
            author = ""
            sections = xmlHelper.getSections(root)

            if len(sections) > 0:
                lastPres = TeiText(x, title, sections, author)
            
            if lastPaper != None and lastPres != None:
                papers.append(lastPaper)
                lastPaper = None
                
                persentations.append(lastPres)
                lastPres = None

    return (papers, persentations)