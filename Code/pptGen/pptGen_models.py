
#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
import re, os, time

from nltk.tokenize import sent_tokenize


datasetPath = '../../dataset3/XMLs/'

#-----------------------------------------Read data--------------------------------------------------------------------

# Grobid documentation (Install/build/Run): https://grobid.readthedocs.io/en/latest/
# Grobid python client github: https://github.com/kermitt2/grobid-client-python

# <div> </div> - Section
# <heade> </head> - Section title
class Section:
    def __init__(self, secTitle: str, paragraphs: List[str]):
        self.secTitle = secTitle
        self.paragraphs = paragraphs
        self.sec_sent_tokenized = []
        for p in paragraphs:
          self.sec_sent_tokenized = self.sec_sent_tokenized + sent_tokenize(p)

class TeiText:
    def __init__(self, id: str, title: str, sections: List[Section]):
        self.sections = sections
        self.id = id
        self.title = title
        self.text_sent_tokenized = []
        for s in sections:
            text = []
            if s.secTitle != None:
                text.append(sent_tokenize(s.secTitle))
            text += s.sec_sent_tokenized

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
        return title

    def getSections(self, root):
        body = root.find(self.createId('text')).find(self.createId('body'))
        sectionList = []
        sections = body.findall(self.createId('div'))
        if len(sections) > 0:
            for sec in sections:
                sectionTitle = sec.find(self.createId('head'))
                if sectionTitle != None:
                    sectionTitle = sectionTitle.text
                
                paragraphs = [p.text for p in sec.findall(self.createId('p'))]
                
                sectionList.append(Section(sectionTitle, paragraphs))

        
        return sectionList

def readData():
    xmlHelper = GrobidXMLParser()
    papers = []
    persentations = []

    for x in os.listdir(datasetPath):
        fullPath = datasetPath+x
        
        if os.path.isfile(fullPath):
            tree = ET.parse(fullPath)
            root = tree.getroot()

            title = xmlHelper.getTitle(root)
            sections = xmlHelper.getSections(root)

            if 'paper' in x:
                papers.append(TeiText(x, title, sections))
            else:
                persentations.append(TeiText(x, title, sections))

    return (papers, persentations)