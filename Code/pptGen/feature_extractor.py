#!/usr/bin/env python3

from pptGen_models import Section, TeiText, filterStopWords, stop_words, stemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.data import find
from bllipparser import RerankingParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import linear_kernel

from numpy import array

import pickle


def tokenize(text):
        stems = [stemmer.stem(t) for t in word_tokenize(text)]
        return stems

#-----------------------------------------Extract features--------------------------------------------------------------------
# Documentations:
#   - https://arxiv.org/pdf/1909.02776.pdf
#   - https://www.ijcai.org/Proceedings/13/Papers/310.pdf

# TODO: http://ceur-ws.org/Vol-1155/paper-07.pdf    ????Ontologies?????

class FeatureExtractor:
    def __init__(self, papers, presentations):
        self.papers = papers
        self.presentations = presentations
        self.train_features, self.vectorizer = self.createVectorizer(papers, presentations)
        model_dir = find('models/bllip_wsj_no_aux').path
        self.parser = RerankingParser.from_unified_model_dir(model_dir)

    def createVectorizer(self, papers, presentations):
        data = [p.text for p in papers] + [p.text for p in presentations]
        vectorizer = TfidfVectorizer(norm='l2',min_df=0, use_idf=True, smooth_idf=True,
                                    sublinear_tf=True, stop_words=stop_words, tokenizer=tokenize,
                                    analyzer='word')

        train_features = vectorizer.fit_transform(data)

        pickle.dump(vectorizer, open('vectorizer.pkl', 'wb'))

        return train_features, vectorizer

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

    def secStopWords(self, section: Section):
        stop_words = []
        for sent in section.sec_sent_word_tokenized:
            l = list(filter(filterStopWords, sent))
            stop_words.append(l)
        return stop_words

    def secStopWorPercentange(self, section: Section):
        stop_words = self.secStopWords(section)
        stop_words_perc = [float((len(stop_words[index]) + 1)/(len(s) + 1) ) for (index, s) in enumerate(section.sec_sent_word_tokenized)]

        return stop_words_perc

    def stopWorPercentange(self, paper: TeiText):
        stopWordPerc = []
        for s in paper.sections:
            stopWordPerc = stopWordPerc + self.secStopWorPercentange(s)
        return stopWordPerc

    def secNonStorWordNumber(self, section: Section):
        secStopWords = self.secStopWords(section)
        secNonStopWords = [ (len(s) - len(secStopWords[index]) + 1)   for (index, s) in enumerate(section.sec_sent_word_tokenized)]
        return  secNonStopWords

    def nonStopWordNumber(self, paper: TeiText):
        nonstopWordNr = []
        for s in paper.sections:
            nonstopWordNr = nonstopWordNr + self.secNonStorWordNumber(s)

        return nonstopWordNr
    
    def secWordNumber(self, section: Section):
        return [ (len(s) + 1) for (index, s) in enumerate(section.sec_sent_word_tokenized)]

    def wordNumber(self, paper: TeiText):
        wordNr = []
        for s in paper.sections:
            wordNr = wordNr + self.secWordNumber(s)
            
        return wordNr

    # https://towardsdatascience.com/overview-of-text-similarity-metrics-3397c4601f50
    def secSimilarityWithTitle(self, section: Section, transformed_title: [float]):
        transformed_sent = self.vectorizer.transform(section.sec_sent_tokenized)
        # https://intellipaat.com/community/1103/python-tf-idf-cosine-to-find-document-similarity
        # cosine_sims = linear_kernel(transformed_title, transformed_sent).flatten()
        cosine_sims = linear_kernel(transformed_title, transformed_sent)

        return cosine_sims

    def similarityWithTitle(self, paper: TeiText):
        if paper.title != None:
            transformed_title = self.vectorizer.transform([paper.title])
        else:
            transformed_title = self.vectorizer.transform(['the'])
        sims = []
        for s in paper.sections:
            if len(s.sec_sent_tokenized) > 0:
                ss = self.secSimilarityWithTitle(s, transformed_title)
                ss = ss.flatten().tolist()
                sims = sims + ss
        return sims

    def secSimilarityWithTile(self, s: Section, transformed_title):
        sims = []
        if len(s.sec_sent_tokenized) > 0:
                ss = self.secSimilarityWithTitle(s, transformed_title)
                ss = ss.flatten().tolist()
                sims = sims + ss
        return sims


    # TODO: do I need to check with every section's title or only the section in which the sentence is
    def similarityWithSecTitle(self, paper: TeiText):
        sims = []
        for s in paper.sections:
            if s.secTitle != None:
                transformed_title = self.vectorizer.transform([s.secTitle])
            else:
                transformed_title = self.vectorizer.transform(['the'])
            if len(s.sec_sent_tokenized) > 0:
                ss = self.secSimilarityWithTitle(s, transformed_title)
                ss = ss.flatten().tolist()
                sims = sims + ss

        return sims
    
    def secSimilarityWithSecTitles(self, s: Section):
        sims = []

        if s.secTitle != None:
            transformed_title = self.vectorizer.transform([s.secTitle])
        else:
            transformed_title = self.vectorizer.transform(['the'])
        if len(s.sec_sent_tokenized) > 0:
            ss = self.secSimilarityWithTitle(s, transformed_title)
            ss = ss.flatten().tolist()
            sims = sims + ss
        
        return sims


    def wordOverlapWithTitles(self, paper: TeiText):
        w_overlap = []
        for s in paper.sections:
            for stemmed_sent in s.sec_sent_stem_tokenized:
                nr = 0
                for w in stemmed_sent:
                    if w in paper.titles:
                        nr += 1
                w_overlap.append(nr)
        return w_overlap
    
    def sectionWordOverlapWithTitles(self, s: Section, paper: TeiText):
        w_overlap = []
        for stemmed_sent in s.sec_sent_stem_tokenized:
                nr = 0
                for w in stemmed_sent:
                    if w in paper.titles:
                        nr += 1
                w_overlap.append(nr)
        return w_overlap

    # TODO: DEPTH -> Maybe Tree.span() not sure what that is tbh
    # https://github.com/BLLIP/bllip-parser/blob/master/python/bllipparser/RerankingParser.py#L62
    def parseTreeFeatures(self, paper: TeiText):
        nounPhrases = []
        verbPhrases = []
        nrSubtrees = []

        for s in paper.sections:
            for sent in s.sec_sent_tokenized:
                # print(sent)
                best_parser = self.parser.parse(sent).get_parser_best()
                if sent == None or best_parser == None: 
                    break
                parsed_sent = best_parser.ptb_parse
                labels = [t.label for t in parsed_sent.all_subtrees() if not t.is_preterminal()]

                nrNoun = 0
                nrVerb = 0
                for l in labels:
                    if (l == 'NP' or l == 'NNP'):
                        nrNoun += 1
                    elif (l == 'VP'):
                        nrVerb += 1
                nounPhrases.append(nrNoun)
                verbPhrases.append(nrVerb)
                nrSubtrees.append(len(labels))
                
        return (nounPhrases, verbPhrases, nrSubtrees)

    def parseSectionTreeFeatures(self, s: Section):
        nounPhrases = []
        verbPhrases = []
        nrSubtrees = []

        for sent in s.sec_sent_tokenized:
                best_parser = self.parser.parse(sent).get_parser_best()
                if sent == None or best_parser == None: 
                    break
                parsed_sent = best_parser.ptb_parse
                labels = [t.label for t in parsed_sent.all_subtrees() if not t.is_preterminal()]

                nrNoun = 0
                nrVerb = 0
                for l in labels:
                    if (l == 'NP' or l == 'NNP'):
                        nrNoun += 1
                    elif (l == 'VP'):
                        nrVerb += 1
                nounPhrases.append(nrNoun)
                verbPhrases.append(nrVerb)
                nrSubtrees.append(len(labels))

        return (nounPhrases, verbPhrases, nrSubtrees)
 
        

    def extractPaperFeatures(self, paper: TeiText):
        f1, f2, f3 ,f4, f5 ,f6, f7, f8, f9, f10 = [], [], [], [], [], [], [], [], [], []

        if paper.title != None:
            transformed_title = self.vectorizer.transform([paper.title])
        else:
            transformed_title = self.vectorizer.transform(['the'])

        for s in paper.sections:
            f1 = f1 + self.secSentencePos(s)
            f2 = f2 + self.secStopWorPercentange(s)
            f3 = f3 + self.secNonStorWordNumber(s)
            f4 = f4 + self.secWordNumber(s)
            f5 = f5 + self.secSimilarityWithTile(s, transformed_title)
            f6 = f6 + self.secSimilarityWithSecTitles(s)
            (np, vp, st) = self.parseSectionTreeFeatures(s)
            f7 = f7 + np
            f8 = f8 + vp
            f9 = f9 + st
            f10 = f10 + self.sectionWordOverlapWithTitles(s, paper)

        scaler = MinMaxScaler()

        f1 = array(f1)
        f2 = array(f2)

        f_scale = array(f3).reshape(-1, 1)
        scaler.fit(f_scale)
        f3 = scaler.transform(f_scale).reshape(len(f3),)
        
        f_scale = array(f4).reshape(-1, 1)
        scaler.fit(f_scale)
        f4 = scaler.transform(f_scale).reshape(len(f4),)

        f5 = array(f5)

        f_scale = array(f6).reshape(-1, 1)
        scaler.fit(f_scale)
        f6 = scaler.transform(f_scale).reshape(len(f6),)

        f_scale = array(f7).reshape(-1, 1)
        scaler.fit(f_scale)
        f7 = scaler.transform(f_scale).reshape(len(f7),)

        f_scale = array(f8).reshape(-1, 1)
        scaler.fit(f_scale)
        f8 = scaler.transform(f_scale).reshape(len(f8),)

        f_scale = array(f9).reshape(-1, 1)
        scaler.fit(f_scale)
        f9 = scaler.transform(f_scale).reshape(len(f9),)

        f_scale = array(f10).reshape(-1, 1)
        scaler.fit(f_scale)
        f10 = scaler.transform(f_scale).reshape(len(f10),)

        features = [list(a) for a in zip(f1, f2, f3, f4, f5, f6, f7, f8, f9, f10)]

        print(features)

        return features

        

    def extractPFeatures(self, paper: TeiText):
        feature1 = self.sentencePos(paper)

        feature2 = self.stopWorPercentange(paper)

        feature3 = self.nonStopWordNumber(paper)
        #length
        feature4 = self.wordNumber(paper)


        feature5 = self.similarityWithTitle(paper)
        
        feature6 = self.similarityWithSecTitle(paper)


        feature7, feature8, feature9 = self.parseTreeFeatures(paper)
    
        feature10 = self.wordOverlapWithTitles (paper)   
        
        # features = []
        # print(len(feature1))
        # print(len(feature2))
        # print(len(feature3))
        # print(len(feature4))
        # print(len(feature5))
        # print(len(feature6))
        # print(len(feature7))
        # print(len(feature8))
        # print(len(feature9))
        # print(len(feature10))
        features = [list(a) for a in zip(feature1, feature2, feature3, feature4, feature5, feature6, feature7, feature8, feature9, feature10)]
        # print(features)
        scaler = MinMaxScaler()
        scaler.fit(features)
        features = scaler.transform(features)

        return features

    def extractFeatures(self):
        paperFeatures = []
        for paper in self.papers:
            if len(paper.sections) > 0:
                print(paper.id)
                features = self.extractPaperFeatures(paper)
                paperFeatures.append(features)   
        
        return paperFeatures

    
    def secSimilarityWithPres(self, section: Section, transformed_pres: [float]):
        transformed_sent = self.vectorizer.transform(section.sec_sent_tokenized)
        # https://intellipaat.com/community/1103/python-tf-idf-cosine-to-find-document-similarity
        # cosine_sims = linear_kernel(transformed_title, transformed_sent).flatten()
        cosine_sims = linear_kernel(transformed_sent, transformed_pres)

        return cosine_sims

    def extractImportanceFeature(self, paper, presentation):
        imp = []
        featurepap = self.sentencePos(paper)
        featurepres = self.sentencePos(presentation)

        transformed_pres_sec = [self.vectorizer.transform(sec.sec_sent_tokenized) for sec in presentation.sections if len(sec.sec_sent_tokenized) > 0]
        for paperSec in paper.sections:
            if len(paperSec.sec_sent_tokenized) > 0:
                sims = []
                for transformed_sec in transformed_pres_sec:
                    sims = self.secSimilarityWithPres(paperSec, transformed_sec)

                l = [max(z) for z in sims]
                imp = imp + l
            
        return imp

    def getImportanceMetrics(self):
        return [self.extractImportanceFeature(self.papers[i], self.presentations[i])  for i in range(0, len(self.papers))]

    def getSentenceLengths(self):
        return [self.wordNumber(self.papers[i]) for i in range(0, len(self.papers))] 