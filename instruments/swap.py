import numpy as np
import matplotlib
import matplotlib.style
matplotlib.use("Qt5Agg")
matplotlib.style.use('classic')
from matplotlib import pyplot as plt
from credit import calculateExpectedExposure

class IRSwap( object ):

    def __init__(self, notional=None, maturity=None, couponfreq=None, fixedRate=None):
        self.notional = notional or 1e6
        self.maturity = maturity or 5
        self.fixedRate = fixedRate or 5.0
        self.couponfreq = couponfreq or 0.5
        self.couponQuantity = int(self.maturity/self.couponfreq)


    def price(self, indexCurve, time, fixedRate=None):
        '''From the fixed rate counterparty point of view'''
        remainingTime = self.maturity - time
        settlementsRemaining = int(round(remainingTime/self.couponfreq,0))
        startingTime = int(round(time / self.couponfreq))
        endTime = int(round(self.maturity / self.couponfreq, 0))
        curveSegment = indexCurve[startingTime:endTime]
        couponsPerYear = round(1/self.couponfreq)

        if startingTime==endTime:
            return 0

        floatRate=curveSegment[0]
        settlements = np.ones(settlementsRemaining)*( -self.fixedRate+floatRate )*self.notional

        powers=np.arange(1,(endTime-startingTime)+1)
        return np.sum( settlements/( ( 1+curveSegment/couponsPerYear )**powers ) )


    def vectorSwapPrice(self,indexCurves,time):
        output = np.empty( [len(indexCurves),len(time)] )
        for i,curve in enumerate(indexCurves):
            f = np.vectorize( lambda t: self.price(curve,t))
            output[i,:]=f(time)
            if i%1000==0:
                print('%s curves simulated'%i)

        return output


def main():
    from curves.curve import regularCurve,monteCarloRateCurve
    ITERATIONS = 10000
    MONTECARLO_SIGMA = 0.25

    myswap= IRSwap(couponfreq=0.01)
    x=np.arange(0,myswap.maturity+myswap.couponfreq,myswap.couponfreq)

    #construir curvas para cada tiempo
    curves=np.zeros([ITERATIONS,myswap.couponQuantity+1])
    for i in range(ITERATIONS):
        curves[i,:] = monteCarloRateCurve(  delta_t=myswap.couponfreq,
                                            numberOfPoints=myswap.couponQuantity+1,
                                            initialValue=myswap.fixedRate,
                                            drift=0,
                                            sigma=MONTECARLO_SIGMA).values

    y=myswap.vectorSwapPrice(curves,x)
    #for output in y:
    #    plt.plot(x,output)
    #plt.show()
    output = calculateExpectedExposure(y)
    plt.plot(x,output)
    plt.show()


main()