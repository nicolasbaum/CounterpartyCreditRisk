from curves.curve import shortRateCIRmodel
from matplotlib import pyplot as plt

model = shortRateCIRmodel(numberOfPoints=1000)
model2=shortRateCIRmodel(numberOfPoints=1000,K=model.K*4)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(model.values,label='K=%s'%(model.K), linewidth=0.7)
ax.plot(model2.values, label='K=%s'%(model2.K), linewidth=0.7)
ax.hlines(y=model.theta,xmin=0,xmax=1000,colors='red',linewidth=1,label='Media=%s'%(model.theta))
ax.set_title('Modelo CIR')
plt.legend(loc='upper left', fontsize=8, framealpha=0.5)

plt.show()