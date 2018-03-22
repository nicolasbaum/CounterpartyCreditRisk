import matplotlib
import matplotlib.style
matplotlib.use("Qt5Agg")
matplotlib.style.use('classic')
from matplotlib import pyplot as \
    plt
import numpy as np
from credit import CreditExposure
from curves.curve import regularCurve,flatCurve,shortRateCIRmodel, zeroCurve, curvesFromModel
from instruments.swap import IRSwap, Swaption

def main():
    ITERATIONS = 10000
    PERCENTILES = [ 0.9, 0.95, 0.99 ]

    #Instanciacion de instrumento
    instrument = Swaption(couponfreq=0.5,maturity=15, strike=0.015)
    timeVector = instrument.generateTimeVector()

    #construir curva original
    yieldCurve = regularCurve().values
    #yieldCurve = flatCurve().values
    baseCurve = zeroCurve( yieldCurve, instrument.couponfreq ).values[:instrument.couponQuantity+1]
    shortRate = baseCurve[0]

    #el fixed paga el float actual para arrancar en MTM=0
    instrument.fixedRate = shortRate

    #Inicializacion de short-rate model
    model = shortRateCIRmodel(
                            deltaT=instrument.couponfreq,
                            numberOfPoints=instrument.couponQuantity + 1,
                            initialValue=shortRate,
                            sigma=shortRate/2)

    #Curvas para scenario generation
    curves = curvesFromModel( model ).generateCurves( baseCurve,ITERATIONS )

    PFEs={}
    strikes = [1.05,1.1,1.2]
    for strike in strikes:
        instrument.strike = strike*shortRate
        mtms=instrument.vectorPrice(curves, timeVector)
        PFEs[strike]=CreditExposure.calculatePFE(mtms, 0.95)

    #Graficos
    colors = iter(plt.get_cmap('cool')(np.linspace(0, 1, len(PFEs))))
    for strike,pfe in PFEs.items():
        plt.plot(timeVector, pfe, linewidth=2, color=next( colors ), label='Strike=%s* r(0)'%str(strike) )

    plt.legend(loc='upper left', fontsize=8, framealpha=0.5)
    plt.show()


main()