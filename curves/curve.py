import numpy as np

class regularCurve( object ):
    def __init__(self,values=None,offset=None):
        self.values = np.array(values) or np.array([1.46,1.60,1.69,1.75,1.81,1.93,2.01,2.06,2.08,2.18,2.25,2.31,2.37,
                                                    2.43,2.48,2.52,2.55,2.58,2.62,2.66,2.70,2.74,2.75,2.78,2.81,2.84,
                                                    2.87,2.90,2.93,2.96,2.99,3.03,3.07,3.11,3.16,3.20,3.22,3.25,3.27,
                                                    3.30,3.33,3.36,3.40,3.43,3.43,])
        if offset:
            self.values+=offset

class monteCarloCurve( object ):
    def __init__(self, delta_t=None, numberOfPoints = None, initialValue = None, drift=None, sigma=None):
        self.initialValue = initialValue or 2.5
        self.delta_t=delta_t or 0.5
        self.n = numberOfPoints or 10
        self.drift = drift or 0
        self.sigma = sigma or 0.1

    @property
    def values(self):
        randomValues = np.random.normal(size=self.n-1)
        result = np.empty(self.n)
        result[0]=self.initialValue
        sqrt_delta_t = (self.delta_t**0.5)
        for i in range(1,self.n):
            result[i]=result[i-1]*(1+self.drift*self.delta_t+self.sigma*sqrt_delta_t*randomValues[i-1])

        return result
