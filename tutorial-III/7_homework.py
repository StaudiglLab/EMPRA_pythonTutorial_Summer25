import numpy as np
import matplotlib.pyplot as plt
#loading only first three columns
ts,left_x,left_y=np.loadtxt('exampleEyetrackerData.tsv',usecols=[0,1,2],unpack=True,skiprows=1)

plt.plot(left_x)
plt.show()

'''
 For the following use only left eye data:
1. Find periods where eyetracker data is bad.
2. Can you think of a plot that can illustrate the bad epochs?
3. Using only the good data, find the
   mean and standard deviation of eye position relative to centre of the screen (in dva).
4. Count the number of times the eyes fixate at a position for more than 200 milliseconds. 
5. Make a plot showing the positions of the above fixation points.
'''