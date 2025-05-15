import numpy as np
import matplotlib.pyplot as plt
#loading only first three columns
ts,left_x,left_y=np.loadtxt('exampleEyetrackerData.tsv',usecols=[0,1,2],unpack=True,skiprows=1)

#TODO: what does the following statement do? 
timeaxis=(ts-ts[0])/1e6

plt.plot(timeaxis,left_x)
plt.show()
