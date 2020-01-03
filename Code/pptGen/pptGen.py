#!/usr/bin/env python3

from pptGen_models import readData
from feature_extractor import FeatureExtractor


# Documentations:
#   - https://arxiv.org/pdf/1909.02776.pdf
#   - https://www.ijcai.org/Proceedings/13/Papers/310.pdf

(pap, pres) = readData()
# print(pap)
# print(pap[0].sections[1].secTitle)

featureExtractor = FeatureExtractor(pap, pres)
features = featureExtractor.extractFeatures()

# print(features)

# print([p.sections for p in pap])