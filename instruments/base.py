import numpy as np

class baseInstrument:

    def vectorPrice(self, indexCurves, time):
        pass

    def generateTimeVector(self):
        return np.arange(0, self.maturity + self.couponfreq, self.couponfreq)