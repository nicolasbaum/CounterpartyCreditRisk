import numpy as np
import matplotlib
import matplotlib.style
matplotlib.use("Qt5Agg")
matplotlib.style.use('classic')
from matplotlib import pyplot as plt
from credit import CreditExposure

class IRSwap( object ):

    def __init__(self, notional=None, maturity=None, couponfreq=None, fixedRate=None):
        self.notional = notional or 1e6
        self.maturity = maturity or 5
        self.fixedRate = fixedRate or 5.0
        self.couponfreq = couponfreq or 0.5
        self.couponQuantity = int(self.maturity/self.couponfreq)


    def price(self, indexCurves, time, fixedRate=None):
        '''From the fixed rate counterparty point of view'''
        remainingTime = self.maturity - time
        settlementsRemaining = int(round(remainingTime/self.couponfreq,0))
        startingTime = int(round(time / self.couponfreq))
        endTime = int(round(self.maturity / self.couponfreq, 0))
        # Number of curve to be applied will be equal to the number of element in the time vector
        numberOfCurve = startingTime
        curveSegment = indexCurves[numberOfCurve,:endTime-startingTime]
        couponsPerYear = round(1/self.couponfreq)

        if startingTime==endTime:
            return 0

        floatRate=curveSegment[0]
        settlements = np.ones(settlementsRemaining)*( -self.fixedRate+floatRate )*self.notional

        powers=np.arange(1,(endTime-startingTime)+1)
        return np.sum( settlements/( ( 1+curveSegment/couponsPerYear )**powers ) )


    def vectorSwapPrice(self,indexCurves,time):
        output = np.empty( [indexCurves.shape[0],len(time)] )
        for i,curves in enumerate(indexCurves):
            output[i,:]=[ self.price(curves,t) for t in time ]
            if i%1000==0:
                print('%s curves simulated'%i)

        return output


def main():
    from curves.curve import regularCurve,shortRateCIRmodel, zeroCurve
    ITERATIONS = 10000

    myswap = IRSwap(couponfreq=0.5,maturity=15)
    x=np.arange(0,myswap.maturity+myswap.couponfreq,myswap.couponfreq)

    #construir curvas para cada tiempo
    #baseCurve = zeroCurve( regularCurve().values, myswap.couponfreq ).values[:myswap.couponQuantity+1]
    baseCurve = regularCurve().values[:myswap.couponQuantity+1]
    shortRate = baseCurve[0]
    myswap.fixedRate = shortRate


    curves=np.zeros([ITERATIONS,myswap.couponQuantity+1,myswap.couponQuantity+1])
    model = shortRateCIRmodel(deltaT=myswap.couponfreq,
                            numberOfPoints=myswap.couponQuantity + 1,
                            initialValue=shortRate,
                            sigma=shortRate/2)
    for i in range(ITERATIONS):
        modelShortRates = model.values
        curves[i,0,:] = baseCurve
        for j in range(1,myswap.couponQuantity+1):
            curves[i,j,:] = baseCurve * ( modelShortRates[j] / shortRate)

    MTMs=myswap.vectorSwapPrice(curves,x)
    PFE = CreditExposure.calculatePFE(MTMs, 0.95)
    EE = CreditExposure.calculateExpectedExposure(MTMs)

    for MTM in MTMs:
        plt.plot(x,MTM,alpha=0.3,linewidth=0.5)
    plt.plot(x, EE, linewidth=2, color='red')
    plt.plot(x, PFE, linewidth=2, color='orange')
    #plt.plot(x,EE,linestyle='None',marker='',markersize=10,color='red')
    #plt.plot(x,PFE,linestyle='None',marker='^',markersize=10,color='yellow')
    plt.show()


main()