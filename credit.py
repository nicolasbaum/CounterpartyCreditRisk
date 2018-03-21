import numpy as np

class CreditExposure:

    @staticmethod
    def transformExposuresGivenCollateral( exposure, threshold, interval ):
        #ToDo: Calcular puntos intermedios dado deltaT para magin call
        pass

    @staticmethod
    def calculateExpectedExposure( expectedMTMs ):
        mtms = expectedMTMs.copy()
        mtms[ np.where(mtms<0) ]=0
        return np.average(mtms,axis=0)

    @staticmethod
    def calculatePFE(expectedMTMs, percentile=None):
        percentile = percentile or 0.95
        numberOfCurvesBelowPercentile = int(percentile*len(expectedMTMs))
        indexes = np.argsort(expectedMTMs, axis=0)[numberOfCurvesBelowPercentile,:]
        return expectedMTMs[ indexes,np.arange(expectedMTMs.shape[1]) ]