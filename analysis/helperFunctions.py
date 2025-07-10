import numpy as np
import pandas as pd
from scipy.stats import ttest_rel

# a function to take a boolean mask and get start and end indices of all True clusters in it.
def getClustersFromMask(mask):
	mask=mask.astype("int")
	if(np.mean(mask)==1.0):
		return np.array([0]),np.array([len(mask)])
	elif(np.mean(mask)==0.0):
		return np.array([0]),np.array([0])
	ediff=(mask[1:]-mask[:-1])#np.ediff1d(mask.astype("int"))
	startIndx=np.arange(len(ediff))[ediff>0]
	stopIndx=np.arange(len(ediff))[ediff<0]
	if(len(startIndx)<len(stopIndx) or (len(stopIndx)>0 and startIndx[0]>stopIndx[0])):
		startIndx=np.append([-1],startIndx)
	if(len(startIndx)>len(stopIndx)):
		stopIndx=np.append(stopIndx,len(ediff))
	return startIndx+1,stopIndx-startIndx

#function to mark samples as invalid around NaNs
def expandNaNs(pos,			#time series of positions
			   window		#number of samples to mark as invalid around each NaN
			   ):
    nanMask=np.isnan(pos)    
    nanMaskExpanded=np.convolve(nanMask,np.ones(window),mode='same')>0    
    pos[nanMaskExpanded]=np.nan
    return pos

#function to mark samples as invalid around NaNs
def getVelocity(pos,			#time series of positions
				smoothWindow=5	#length of smoothing window
				):
	#get difference between consequetive positions
    velocity=np.ediff1d(pos,to_end=0)
	#smoothing over 5 sample points 
    velocity=np.convolve(velocity,np.ones(smoothWindow)/smoothWindow,mode='same')
    return velocity

def getSignificantMask(seriesA,seriesB, #the two series to compare
					   pvalThresh,		#pvalue thereshold for signifance
					   ):
	res=ttest_rel(seriesA,seriesB,axis=0)
	nIndependentTests=len(res.pvalue)
	significantMask=res.pvalue<pvalThresh/nIndependentTests  #Bonferroni correction for multiple comparisions
	return significantMask