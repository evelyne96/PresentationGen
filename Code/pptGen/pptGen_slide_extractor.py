#!/usr/bin/env python3
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk import RegexpParser
from nltk import Tree
from nltk.stem import SnowballStemmer

import numpy as np
from scipy import spatial
import gensim

from nltk.stem import WordNetLemmatizer 
  
lemmatizer = WordNetLemmatizer()

#Load Google's pre-trained Word2Vec 
word2vec = gensim.models.KeyedVectors.load_word2vec_format('./w2vmodel/GoogleNews-vectors-negative300.bin', binary=True) 
index2word_set = set(word2vec.wv.index2word)

def avg_feature_vector(sentence, model, num_features, index2word_set):
    words = word_tokenize(sentence)
    feature_vec = np.zeros((num_features, ), dtype='float32')
    n_words = 0
    for word in words:
        word_lem = lemmatizer.lemmatize(word)
        if word in index2word_set:
            n_words += 1
            feature_vec = np.add(feature_vec, model[word])
    if (n_words > 0):
        feature_vec = np.divide(feature_vec, n_words)
    return feature_vec

def sent_similarity(r_sent, l_sent):
    s1_afv = avg_feature_vector(r_sent, model=word2vec, num_features=300, index2word_set=index2word_set)
    s2_afv = avg_feature_vector(l_sent, model=word2vec, num_features=300, index2word_set=index2word_set)
    sim = 1 - spatial.distance.cosine(s1_afv, s2_afv)

    return sim


# https://www.nltk.org/book/ch07.html
# TODO: write about chunking and extracting noun phrases, grammar etc

# Defining a grammar & Parser
NP = "NP: {(<V\w+>|<NN\w?>)+.*<NN\w?>}"
grammar = r"""
    NBAR:
        # Nouns and Adjectives, terminated with Nouns
        {<NN.*>+<NN.*>}
        {<JJ.*>+<NN.*>}
        {<NNP>+}
        {<JJ.*>+<NNP.*>}
        {<NNP.*>+<NNP.*>}
        {<DT.*>*<JJ>+<NN.*>}
        {<DT.*>*<JJ>+<NNP.*>}


    NP:
        {<NBAR>}
        # Above, connected with in/of/etc...
        {<NBAR><IN><NBAR>}
    """

chunker = RegexpParser(grammar)

def get_continuous_chunks(text, chunk_func=ne_chunk):
    chunked = chunk_func(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []

    for tree in chunked.subtrees(filter=lambda t: t.label() == 'NP'):
        continuous_chunk.append(' '.join([child[0] for child in tree.leaves()]))
    return continuous_chunk

def generate_np_chunks(data):
    np_chunks = []
    for (k, sent) in data:
        chunk = get_continuous_chunks(sent, chunk_func=chunker.parse)
        # chunk = get_continuous_chunks(sent)
        np_chunks.append(chunk)

    return np_chunks

def rank_np_chunks(np_chunks, sents, paper):
    chunk_ocs = []

    for i in range(len(sents)):
        # print(np_chunks[i], sents[i])
        chunks = np_chunks[i]
        (sec, sent) = sents[i]

        if len(chunks) > 0:
            inner_chunk_ocs = []
            for j in range(len(chunks)):
                c = chunks[j]
                chunk_oc = 0
                for s in paper.sections:
                    for sent in s.sec_sent_tokenized:
                        chunk_oc += sent.count(c)
                
                inner_chunk_ocs.append((chunk_oc, c, sec))
            chunk_ocs.append(inner_chunk_ocs)
        else:
            chunk_ocs.append([])

    # print(sents)
    # print(chunk_ocs)
    return chunk_ocs


# note this could be done by using similarity of the nps or the sentences
# we should try both
def np_chunk_close(r_chunks, l_chunks):
    for (r_chunk_oc, r_c, r_sec) in r_chunks:
        for (l_chunk_oc, l_c, l_sec) in l_chunks:
            if r_sec != l_sec:
                return False
            if l_chunk_oc > 1 or r_chunk_oc > 1:
                sim = sent_similarity(r_c, l_c)
                if sim > 0.65:
                    return True
    return False

# [ ("First Frame",  [("title",["ONE", "TWO", "THREe"]), 
#                     (None, ["First", "Second"])]
#   )
# ]
def create_pres_points(chunks, sents, paper):
    frames = []
    points = []
    i = 0
    while i < len(sents)-1:
        chunk_oc = chunks[i]
        s = sents[i]
        j = i
        l_chunk_oc = chunks[j]
        # collect elements that are near each other and are in the same section at least? and are continuous
        # from i to j elements should be put into the same bullet point
        # look up np with the biggest freq from i to j that will be the first point
        # then all the sentences will go under that point
        while np_chunk_close(chunk_oc, l_chunk_oc):
            j += 1
            l_chunk_oc = chunks[j]
        if (i == j):
            points.append((None, [s]))
        else:
            second_ps = sents[i:j+1]
            max_rank = 0
            max_rank_c = None
            for k in range(i, j):
                chunk = chunks[k]
                for (c_oc, c, sec) in chunk:
                    if c_oc > max_rank:
                        max_rank = c_oc
                        max_rank_c = (c_oc, c, sec)
            (rank, max_rank_title, sec) = max_rank_c
            points.append((max_rank_title, [second_ps]))
        
        i = j+1

    for p in points:
        print(p)




        

#first level bullet noun phrases

# A clause is the basic unit of grammar. Typically a main clause is made up of a subject (s) (a noun phrase)
#  and a verb phrase (v). Sometimes the verb phrase is followed by other elements, e.g objects (o), complements (c), adjuncts (ad).
#   These other elements are sometimes essential to complete the meaning of the clause:

