#!/usr/bin/env python3

from pptGen_models import readData, readPData, readData2
from feature_extractor import FeatureExtractor
from lin_prog_solver import ILPSummarizer

import pickle
import sys, getopt
from numpy import array


# Documentations:
#   - https://arxiv.org/pdf/1909.02776.pdf
#   - https://www.ijcai.org/Proceedings/13/Papers/310.pdf


feature_file = 'features_2.pkl'
score_file = 'scores_2.pkl'


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"frt")
    except getopt.GetoptError:
        print('pptGen.py -option where option [-f|-r] f=read and extract features r=read existent features')
        sys.exit(2)

    (pap, pres) = readData2()
    for opt, arg in opts:
      if opt == '-f':
        featureExtractor = FeatureExtractor(pap, pres)
        features = featureExtractor.extractFeatures()
        pickle.dump(features, open(feature_file, 'wb'))
        scores = featureExtractor.getImportanceMetrics()
        pickle.dump(scores, open(score_file, 'wb'))

        print(features)
        print(scores)
      if opt == '-r':
        features = pickle.load(open( feature_file, "rb" ))
        scores = pickle.load(open(score_file, "rb"))
        

        # print(len(features))
        # print(scores)

      if opt == '-t':
          readData2()
        #   featureExtractor = FeatureExtractor(pap, pres)
        #   featureExtractor.extractPaperFeatures(pap[0])

    # p2 = features[2]
    
    featureExtractor = FeatureExtractor(pap, pres)
    sentenceLengths = featureExtractor.getSentenceLengths()

    index = 15
    for i in range(0, len(pap)):
        print(pap[i].id)
        if pap[i].id == "0000-0000-0000_0_paper.tei.xml":
            index = i
            break

    s2 = scores[index]
    s2Lengths = sentenceLengths[index]
    p2 = pap[index]

    print(len(s2), len(s2Lengths))
    ilp_sum = ILPSummarizer(sentence_importance=s2, sentence_lengths=s2Lengths, maxlen=450)
    solution = ilp_sum.solve_summ()

    sents = p2.getSentences(solution)

    #we have the sentences now we need the discourse analysis for the grouping
    print(sents)
    


if __name__ == "__main__":
   main(sys.argv[1:])

# p = readPData('0000-0002-7644-5327_15_paper.tei.xml')
# print(p)

# if p != None:
#     featureExtractor = FeatureExtractor([p], [p])
#     f = featureExtractor.extractPFeatures(p)
#     print(f)


