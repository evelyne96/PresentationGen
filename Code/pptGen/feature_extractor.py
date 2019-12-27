#!/usr/bin/env python3

from pptGen_models import Section, TeiText

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

#-----------------------------------------Extract features--------------------------------------------------------------------
# Documentations:
#   - https://arxiv.org/pdf/1909.02776.pdf
#   - https://www.ijcai.org/Proceedings/13/Papers/310.pdf

class FeatureExtractor:
    def __init__(self, papers, presentations):
        self.papers = papers
        self.presentations = presentations

    def secSentencePos(self, section: Section):
        secLen = len(section.sec_sent_tokenized) + 1
        sectPos = [float((index + 1)/secLen ) for (index, s) in enumerate(section.sec_sent_tokenized)]

        return sectPos

    # check Cosine position from: https://arxiv.org/pdf/1909.02776.pdf
    def sentencePos(self, paper: TeiText):
        secSentPos = [] 
        for s in paper.sections:
            secSentPos = secSentPos + self.secSentencePos(s)
        return secSentPos
    
    def extractFeatures(self):
        features = []
        feature1 = self.sentencePos(self.papers[0])
    
        return features
