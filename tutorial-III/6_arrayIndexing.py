import numpy as np
import matplotlib.pyplot as plt
#loading only first three columns
ts,left_x,left_y=np.loadtxt('exampleEyetrackerData.tsv',usecols=[0,1,2],unpack=True,skiprows=1)

plt.plot(left_x)
plt.show()

#TODO in class: show selection with index over an interesting range in data

#TODO in class: plot the data after selecting a range

#TODO in class: show how to skip samples

#TODO in class: array masking examples(enough time?)