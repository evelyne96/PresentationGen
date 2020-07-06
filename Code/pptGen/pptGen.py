#!/usr/bin/env python3

from pptGen_models import readData, readPData, readData2
from feature_extractor import FeatureExtractor
from lin_prog_solver import ILPSummarizer
from pptGen_slide_extractor import generate_np_chunks, rank_np_chunks, create_pres_points

import pickle
import sys, getopt
from numpy import array


# Documentations:
#   - https://arxiv.org/pdf/1909.02776.pdf
#   - https://www.ijcai.org/Proceedings/13/Papers/310.pdf


feature_file = './pickles/features.pkl'
score_file = './pickles/scores.pkl'


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"frt")
    except getopt.GetoptError:
        print('pptGen.py -option where option [-f|-r|-t] f=read and extract features r=read existent features t=test')
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

      # if opt == '-t':
        # readData2()
        #   featureExtractor = FeatureExtractor(pap, pres)
        #   featureExtractor.extractPaperFeatures(pap[0])

    # p2 = features[2]
    

    ######TEST######

    # featureExtractor = FeatureExtractor(pap, pres)
    # sentenceLengths = featureExtractor.getSentenceLengths()

    # index = 15
    # for i in range(0, len(pap)):
    #     print(pap[i].id)
    #     if pap[i].id == "0000-0000-0000_0_paper.tei.xml":
    #         index = i
    #         break

    # s2 = scores[index]
    # s2Lengths = sentenceLengths[index]
    # p2 = pap[index]

    # print(len(s2), len(s2Lengths))
    # ilp_sum = ILPSummarizer(sentence_importance=s2, sentence_lengths=s2Lengths, maxlen=450)
    # solution = ilp_sum.solve_summ()

    # sents = p2.getSentences(solution)
    # np_chunks = generate_np_chunks(sents)
    # ranked_np_chunks = rank_np_chunks(np_chunks, sents, p2)
    # create_pres_points(ranked_np_chunks, sents, p2)

    ######TEST######
    


if __name__ == "__main__":
   main(sys.argv[1:])



# test_paper = "0000-0000-0000_0_pres.xml"
# test_tei_paper = readPData(test_paper, isPaper=False)
# print(test_tei_paper.text)

# if p != None:
#     featureExtractor = FeatureExtractor([p], [p])
#     f = featureExtractor.extractPFeatures(p)
#     print(f)


