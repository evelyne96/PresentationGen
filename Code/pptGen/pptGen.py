#!/usr/bin/env python3

from pptGen_models import readData
from feature_extractor import FeatureExtractor




(pap, pres) = readData()
featureExtractor = FeatureExtractor(pap, pres)
features = featureExtractor.extractFeatures()
# print(features)

# print([p.sections for p in pap])