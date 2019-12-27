#!/usr/bin/env python3

# from xml.dom import minidom
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
import re, os, time

datasetPath = '../dataset3/XMLs/'

# <div> </div> - Section
# <heade> </head> - Section title
class Section:
    def __init__(self, secTitle: str, paragraphs: List[str]):
        self.secTitle = secTitle
        self.paragraphs = paragraphs

class TeiText:
    def __init__(self, title: str, sections: List[Section]):
        self.sections = sections
        self.title = title

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
            # print(title)
            sections = xmlHelper.getSections(root)

            if 'paper' in x:
                papers.append(TeiText(title, sections))
            else:
                persentations.append(TeiText(title, sections))

    return (papers, persentations)

(pap, pres) = readData()

# print([p.sections for p in pap])