import datetime
import math

import numpy as np


class regularCurve( object ):
    def __init__(self,values=None,offset=None):
        self.values = np.array(values) or np.array([1.46,1.60,1.69,1.75,1.81,1.93,2.01,2.06,2.08,2.18,2.25,2.31,2.37,
                                                    2.43,2.48,2.52,2.55,2.58,2.62,2.66,2.70,2.74,2.75,2.78,2.81,2.84,
                                                    2.87,2.90,2.93,2.96,2.99,3.03,3.07,3.11,3.16,3.20,3.22,3.25,3.27,
                                                    3.30,3.33,3.36,3.40,3.43,3.43,])/100
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
        sqrt_delta_t = math.sqrt(sef.delta_t)
        for i in range(1,self.n):
            result[i]=result[i-1]*(1+self.drift*self.delta_t+self.sigma*sqrt_delta_t*randomValues[i-1])
        return result

class curvesFromModel( object ):
    def __init__(self, model):
        self.model = model

    def generateCurves(self, baseCurve, iterations):
        shortRate = baseCurve[0]
        curves = np.zeros([iterations, self.model.n, self.model.n])
        for i in range(iterations):
            modelShortRates = self.model.values
            curves[i, 0, :] = baseCurve
            for j in range(1, self.model.n):
                curves[i, j, :] = baseCurve * ( modelShortRates[j] / shortRate )

        return curves

class shortRateCIRmodel( object ):
    def __init__(self, numberOfPoints = None, deltaT=None, initialValue=None, K=None, theta=None, sigma=None):
        '''
        K: Speed of mean-reversion
        theta: Mean around model reverts
        sigma: Deviation of Wiener process
        '''
        self.seed = int( (datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds() )
        self.deltaT = deltaT or 0.5
        self.initialValue = initialValue or 0.0146
        self.K = K or 0.2
        self.theta = theta or self.initialValue
        self.sigma = sigma or 0.012
        self.n = numberOfPoints or 10

        np.random.seed(self.seed)

    @property
    def values(self):
        randomValues = np.random.normal(size=self.n - 1)
        result = np.empty(self.n)
        result[0]=self.initialValue
        for i in range(1,self.n):
            result[i]=result[i-1]+self.K*(self.theta-result[i-1])*self.deltaT+self.sigma*math.sqrt(result[i-1])*randomValues[i-1]

        return result

class zeroCurve( object ):
    def __init__(self, yieldCurve, deltaT):
        """ Bootstrapping the yield curve """
        bootstrapper=BootstrapYieldCurve()
        for i,yld in enumerate(yieldCurve):
            bootstrapper.add_instrument(100,(i+1)*deltaT,yld*100,100,int(round(1/deltaT)))

        self.values = np.array( bootstrapper.get_zero_rates() )

class BootstrapYieldCurve(object):

    def __init__(self):
        self.zero_rates = dict()  # Map each T to a zero rate
        self.instruments = dict()  # Map each T to an instrument

    def add_instrument(self, par, T, coup, price,
                       compounding_freq=2):
        """  Save instrument info by maturity """
        self.instruments[T] = (par, coup, price, compounding_freq)

    def get_zero_rates(self):
        """  Calculate a list of available zero rates """
        self.__bootstrap_zero_coupons__()
        self.__get_bond_spot_rates__()
        return [self.zero_rates[T] for T in self.get_maturities()]

    def get_maturities(self):
        """ Return sorted maturities from added instruments. """
        return sorted(self.instruments.keys())

    def __bootstrap_zero_coupons__(self):
        """ Get zero rates from zero coupon bonds """
        for T in self.instruments:
            (par, coup, price, freq) = self.instruments[T]
            if coup == 0:
                self.zero_rates[T] = \
                    self.zero_coupon_spot_rate(par, price, T)

    def __get_bond_spot_rates__(self):
        """ Get spot rates for every marurity available """
        for T in self.get_maturities():
            instrument = self.instruments[T]
            (par, coup, price, freq) = instrument

            if coup != 0:
                self.zero_rates[T] = \
                    self.__calculate_bond_spot_rate__(
                        T, instrument)

    def __calculate_bond_spot_rate__(self, T, instrument):
        """ Get spot rate of a bond by bootstrapping """
        try:
            (par, coup, price, freq) = instrument
            periods = T * freq  # Number of coupon payments
            value = price
            per_coupon = coup / freq  # Coupon per period

            for i in range(int(periods) - 1):
                t = (i + 1) / float(freq)
                spot_rate = self.zero_rates[t]
                discounted_coupon = per_coupon * \
                                    math.exp(-spot_rate * t)
                value -= discounted_coupon

            # Derive spot rate for a particular maturity
            last_period = int(periods) / float(freq)
            spot_rate = -math.log(value /
                                  (par + per_coupon)) / last_period
            return spot_rate

        except:
            print
            "Error: spot rate not found for T=%s" % t

    def zero_coupon_spot_rate(self, par, price, T):
        """ Get zero rate of a zero coupon bond """
        spot_rate = math.log(par / price) / T
        return spot_rate


