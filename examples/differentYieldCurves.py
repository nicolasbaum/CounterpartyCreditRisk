import matplotlib
import matplotlib.style
matplotlib.use("Qt5Agg")
matplotlib.style.use('classic')
from matplotlib import pyplot as \
    plt
import numpy as np
from credit import CreditExposure
from curves.curve import regularCurve,flatCurve,invertedCurve,shortRateCIRmodel, zeroCurve, curvesFromModel
from instruments.swap import IRSwap, Swaption

def main():
    ITERATIONS = 10000

    #Instanciacion de instrumento
    instrument = IRSwap(couponfreq=0.5,maturity=15)
    timeVector = instrument.generateTimeVector()

    baseCurves = {}
    yieldCurve = regularCurve().values
    baseCurves['regular'] =  zeroCurve( yieldCurve, instrument.couponfreq ).values[:instrument.couponQuantity+1]
    yieldCurve = flatCurve().values
    baseCurves['flat'] = zeroCurve( yieldCurve, instrument.couponfreq ).values[:instrument.couponQuantity+1]
    yieldCurve = invertedCurve().values
    baseCurves['inverted'] = zeroCurve(yieldCurve, instrument.couponfreq).values[:instrument.couponQuantity + 1]

    shortRate = baseCurves['regular'][0]

    #el fixed paga el float actual para arrancar en MTM=0
    instrument.fixedRate = shortRate

    #Inicializacion de short-rate model
    model = shortRateCIRmodel(
                            deltaT=instrument.couponfreq,
                            numberOfPoints=instrument.couponQuantity + 1,
                            initialValue=shortRate,
                            sigma=shortRate/2)

    PFEs={}
    for curveType, baseCurve in baseCurves.items():
        curves= curvesFromModel( model ).generateCurves( baseCurve,ITERATIONS )
        mtms=instrument.vectorPrice(curves, timeVector)
        PFEs[curveType]=CreditExposure.calculatePFE(mtms, 0.95)

    #Graficos
    colors = iter(plt.get_cmap('cool')(np.linspace(0, 1, len(PFEs))))
    for baseCurve,pfe in PFEs.items():
        plt.plot(timeVector, pfe, linewidth=2, color=next( colors ), label='PFE 95% @ '+baseCurve )

    plt.legend(loc='upper left', fontsize=8, framealpha=0.5)
    plt.show()


main()