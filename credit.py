import numpy as np

def calculateExpectedExposure(expectedMTMs):
    expectedMTMs[ np.where(expectedMTMs<0) ]=0
    return np.average(expectedMTMs,axis=0)