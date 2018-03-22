import numpy as np

class IRSwap( object ):

    def __init__(self, notional=None, maturity=None, couponfreq=None, fixedRate=None, floatRate = None, **kwargs):
        self.notional = notional or 1e6
        self.maturity = maturity or 5
        self.fixedRate = fixedRate or 0.05
        self.couponfreq = couponfreq or 0.5
        self.couponQuantity = int(self.maturity/self.couponfreq)
        self.floatRate = floatRate or 0.05


    def price(self, indexCurves, time, startInZero=True):
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

        floatRate=curveSegment[0] if startInZero else self.floatRate
        settlements = np.ones(settlementsRemaining)*( -self.fixedRate+floatRate )*self.notional

        powers=np.arange(1,(endTime-startingTime)+1)
        return np.sum( settlements/( ( 1+curveSegment/couponsPerYear )**powers ) )


    def vectorPrice(self, indexCurves, time):
        output = np.empty( [indexCurves.shape[0],len(time)] )
        for i,curves in enumerate(indexCurves):
            output[i,:]=[ self.price(curves,t) for t in time ]
            if i%1000==0:
                print('%s curves simulated'%i)

        return output

    def generateTimeVector(self):
        return np.arange(0, self.maturity + self.couponfreq, self.couponfreq)


class Swaption( IRSwap ):
    def __init__(self, strike= None, **kwargs):
        super().__init__(**kwargs)
        self.strike = strike or self.floatRate*1.1

    def vectorPrice(self, indexCurves, time):
        n=len(time)
        output = np.zeros([indexCurves.shape[0],n ])
        for i,curves in enumerate(indexCurves):
            overStrike = np.argwhere( curves[:,0] >= self.strike )
            if len(overStrike)>0:
                overStrike = overStrike[0][0]
                output[i, :] = np.where( range(n) >= overStrike, np.array([ self.price(curves, t) for t in time]), 0  )
            if i%1000==0:
                print('%s curves simulated'%i)

        return output



