#!/usr/bin/env python3

from pptGen_models import Section, TeiText, filterStopWords, stop_words, stemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.data import find
from bllipparser import RerankingParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


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
        cosine_sims = linear_kernel(transformed_title, transformed_sent).flatten()

        return cosine_sims.tolist()

    def similarityWithTitle(self, paper: TeiText):
        if paper.title != None:
            transformed_title = self.vectorizer.transform([paper.title])
        else:
            transformed_title = self.vectorizer.transform(['the'])
        sims = []
        for s in paper.sections:
            sims = sims + self.secSimilarityWithTitle(s, transformed_title)
        return sims

    # TODO: do I need to check with every section's title or only the section in which the sentence is
    def similarityWithSecTitle(self, paper: TeiText):
        sims = []
        for s in paper.sections:
            if s.secTitle != None:
                transformed_title = self.vectorizer.transform([s.secTitle])
            else:
                transformed_title = self.vectorizer.transform(['the'])
            
            sims = sims + self.secSimilarityWithTitle(s, transformed_title)

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

    # TODO: DEPTH -> Maybe Tree.span() not sure what that is tbh
    # https://github.com/BLLIP/bllip-parser/blob/master/python/bllipparser/RerankingParser.py#L62
    def parseTreeFeatures(self, paper: TeiText):
        nounPhrases = []
        verbPhrases = []
        nrSubtrees = []

        for s in paper.sections:
            for sent in s.sec_sent_tokenized:
                parsed_sent = self.parser.parse(sent).get_parser_best().ptb_parse
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


    def extractFeatures(self):
        feature1 = self.sentencePos(self.papers[0])
        feature2 = self.stopWorPercentange(self.papers[0])
        feature3 = self.nonStopWordNumber(self.papers[0])
        #length
        feature4 = self.wordNumber(self.papers[0])
        feature5 = self.similarityWithTitle(self.papers[0])
        feature6 = self.similarityWithSecTitle(self.papers[0])
        feature7, feature8, feature9 = self.parseTreeFeatures(self.papers[0])
        feature10 = self.wordOverlapWithTitles (self.papers[0])   

        features = [list(a) for a in zip(feature1, feature2, feature3, feature4, feature5, feature6, feature7, feature8, feature9, feature10)]
        print(features)
        return features