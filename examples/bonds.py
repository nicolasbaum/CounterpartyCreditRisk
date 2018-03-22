import matplotlib
import matplotlib.style
matplotlib.use("Qt5Agg")
matplotlib.style.use('classic')
from matplotlib import pyplot as \
    plt
import numpy as np
from credit import CreditExposure
from curves.curve import regularCurve,flatCurve,shortRateCIRmodel, zeroCurve, curvesFromModel
from instruments.bond import Bond

def main():
    ITERATIONS = 10000
    PERCENTILES = [ 0.9, 0.95, 0.99 ]

    #Instanciacion de instrumento
    instrument = Bond(couponfreq=0.5,maturity=15)
    timeVector = instrument.generateTimeVector()

    # construir curva original
    baseCurve = zeroCurve(regularCurve().values, instrument.couponfreq).values[:instrument.couponQuantity + 1]
    shortRate = baseCurve[0]

    # el fixed paga el float actual para arrancar en MTM=0
    instrument.fixedRate = shortRate

    # Inicializacion de short-rate model
    model = shortRateCIRmodel(
        deltaT=instrument.couponfreq,
        numberOfPoints=instrument.couponQuantity + 1,
        initialValue=shortRate,
        sigma=shortRate / 2)

    # Curvas para scenario generation
    curves = curvesFromModel(model).generateCurves(baseCurve, ITERATIONS)

    # MTMs para scenarios
    MTMs = instrument.vectorPrice(curves, timeVector)

    # Calculo credit risk
    PFEs = [CreditExposure.calculatePFE(MTMs, percentile) for percentile in PERCENTILES]
    EE = CreditExposure.calculateExpectedExposure(MTMs)

    # Graficos
    for MTM in MTMs:
        plt.plot(timeVector, MTM, alpha=0.3, linewidth=0.5)
    plt.plot(timeVector, EE, linewidth=2, color='red')

    colors = iter(plt.get_cmap('cool')(np.linspace(0, 1, len(PFEs))))
    for i, pfe in enumerate(PFEs):
        plt.plot(timeVector, pfe, linewidth=2, color=next(colors), label='PFE@' + str(PERCENTILES[i]) + '%')

    plt.legend(loc='upper left', fontsize=8, framealpha=0.5)  # .get_frame().set_facecolor('grey')
    plt.show()


main()