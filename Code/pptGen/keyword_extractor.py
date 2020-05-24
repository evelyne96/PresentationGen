#!/usr/bin/env python3

# Doc:
# https://pdfs.semanticscholar.org/5a58/00deb6461b3d022c8465e5286908de9f8d4e.pdf
# https://pypi.org/project/rake-nltk/

from rake_nltk import Rake, Metric
from pptGen_models import stop_words
import string

# If you want to control the max or min words in a phrase, for it to be
# considered for ranking you can initialize a Rake instance as below:
# If you want to control the metric for ranking. Paper uses d(w)/f(w) as the
# metric. You can use this API with the following metrics:
# 1. d(w)/f(w) (Default metric) Ratio of degree of word to its frequency.
# 2. d(w) Degree of word only.
# 3. f(w) Frequency of word only.

r = Rake(stopwords=stop_words, punctuations=string.punctuation, ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO, min_length=1, max_length=5)
# r = Rake(ranking_metric=Metric.WORD_DEGREE)
# r = Rake(ranking_metric=Metric.WORD_FREQUENCY)


def extract_score_keywords(text):
    r.extract_keywords_from_text(text)
    r_phrase_score = r.get_ranked_phrases_with_scores()

    return r_phrase_score

def extract_keywords(text):
    r.extract_keywords_from_text(text)
    r_phrases = r.get_ranked_phrases()

    return r_phrases


t = '''Keyphrase  extraction  is  the  task  of  identifying  single  or  multi-word 
        expressions that  represent  the  main  topics  of  a  document.In  this  paper  we  present  TopicRank, 
        a  graphbased  keyphrase  extraction  method  that  relies  on  a  topical  representation  of  the  document. 
        Candidate keyphrases  are  clustered  into  topics  andused  as  vertices  in  a  complete  graph.   
        A graphbased  ranking  model  is  applied  toassign  a significance  score  to each  topic.
        Keyphrases  are  then generated  by selecting  a  candidate  from  each  of  the  topranked topics.  
        We conducted experiments on  four  evaluation  datasets  of  different languages  and  domains.
        Results  show that  TopicRank  significantly  outperforms stateoftheart methods on three datasets'''


s_k = extract_score_keywords(t)
print(s_k)

