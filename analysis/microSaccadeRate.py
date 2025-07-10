import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from helperFunctions import getSignificantMask
def getSaccadeTimestamps(pID,maxAmp,maxVelocity,minInterSaccadicIntervalInMs):
    dfSaccades=pd.read_csv("./datafiles/saccades/task_Enigma_%s_s1_saccades.csv"%(pID))   
    interSaccadicInterval=dfSaccades['startTime'].values[1:]-dfSaccades['stopTime'].values[:-1]  
    dfSaccades=dfSaccades[1:]
    dfSaccades=dfSaccades[np.logical_and.reduce((interSaccadicInterval>minInterSaccadicIntervalInMs/1e3,dfSaccades['amplitude']<maxAmp,dfSaccades['peakVelocity']<maxVelocity))].reset_index(drop=True)
    saccadeTimestamps=dfSaccades['startTime']
    return saccadeTimestamps

def getButtonPressTimestamps(pID,isControlBlock):
    dfTriggers=pd.read_csv("./datafiles/triggerInfo/task_Enigma_%s_s1_Triggers.csv"%(pID))

    #drop practice blocks
    dfTriggers=dfTriggers[np.logical_not(dfTriggers['blockID']=='pract')].reset_index(drop=True)
    dfTriggers['blockID']=dfTriggers['blockID'].values.astype("int")

    if(isControlBlock):
        dfTriggers=dfTriggers[dfTriggers['blockID']>=4].reset_index(drop=True)
    else:
        dfTriggers=dfTriggers[dfTriggers['blockID']<4].reset_index(drop=True)
    dfTriggers=dfTriggers[np.logical_or(dfTriggers['triggerName']=='keyPress_Right',dfTriggers['triggerName']=='keyPress_Left')]
    buttonPressTimestamps=dfTriggers['timestamp_tobii'].values/1e6
    return buttonPressTimestamps


def transitionLockedMicroSaccadeRate(pID,
                                     isControlBlock,
                                     maxAmp,
                                     maxVelocity,
                                     minInterSaccadicIntervalInMs,
                                     binTrialInMs,
                                     smoothWindwInMs,
                                     timeAxisRange):
    
   
    saccadeTimestamps=getSaccadeTimestamps(pID=pID,
                                           maxAmp=maxAmp,
                                           maxVelocity=maxVelocity,
                                           minInterSaccadicIntervalInMs=minInterSaccadicIntervalInMs)

    

    buttonPressTimeStamps=getButtonPressTimestamps(pID=pID,
                                                   isControlBlock=isControlBlock)

 
    nTransitions=len(buttonPressTimeStamps)
    #bin edges
    taxisTrialBins=np.arange(timeAxisRange[0]-smoothWindwInMs,timeAxisRange[1]+smoothWindwInMs+1,binTrialInMs)
    #central point of each bin
    taxisTrialCentral=(taxisTrialBins[1:]+taxisTrialBins[:-1])/2.

    saccadeRate=np.zeros((nTransitions,len(taxisTrialCentral)),dtype='float')

    smoothWindow=int(smoothWindwInMs//binTrialInMs)
    
    for i in range(0,nTransitions):
        t0=buttonPressTimeStamps[i]
        saccadeRate[i],t=np.histogram((saccadeTimestamps-t0)*1e3,bins=taxisTrialBins)

        #avoiding double counting of the same saccades (following Troncoso et al. 2008)
        #blank out everything beyond the neighbouring transitions
        if(i==0):
            prevTransTimestamp=0
        else:
            prevTransTimestamp=buttonPressTimeStamps[i-1]
        if(i==len(buttonPressTimeStamps)-1):
            nextTransTimestamp=np.inf
        else:
            nextTransTimestamp=buttonPressTimeStamps[i+1]
        nanMask=np.logical_or(taxisTrialCentral/1e3<prevTransTimestamp-t0,taxisTrialCentral/1e3>nextTransTimestamp-t0)
        saccadeRate[i,nanMask]=np.nan
        
    
    #get mean saccade rate across all trials
    saccadeRateMean=np.nanmean(saccadeRate,axis=0)

    #smooth mean saccade rate curve
    saccadeRateMean=np.convolve(saccadeRateMean,np.ones(smoothWindow,dtype='float')/smoothWindow,mode='same')
    
    #select timerange
    selmaskTime=np.logical_and(taxisTrialCentral>=timeAxisRange[0],taxisTrialCentral<=timeAxisRange[1])
    taxisTrialCentral=taxisTrialCentral[selmaskTime]

    saccadeRateMean=saccadeRateMean[selmaskTime]
    #baseline correction
    saccadeRateMean=saccadeRateMean/np.nanmean(saccadeRateMean[taxisTrialCentral<-2000])-1

    
    return nTransitions,taxisTrialCentral,saccadeRateMean

def plotMicrosaccadeRate(whichCohort='full',
                 maxAmp=2,
                 maxVelocity=200,
                 minInterSaccadicIntervalInMs=150,
                 binTrialInMs=2,
                 smoothWindwInMs=200,
                 timeAxisRange=[-4000,2000]):
    dfReactionTimes=pd.read_csv("./datafiles/reactionTimes.csv")
    if(whichCohort=='full'):
        pIDs=dfReactionTimes['pID'].values
    else:
        selmask=dfReactionTimes['GroupID']==whichCohort
        if(np.sum(selmask)==0):
            print("No participants found. Please make sure that the group ID is correct")
            return -1
        dfReactionTimes=dfReactionTimes[selmask].reset_index(drop=True)
        pIDs=dfReactionTimes['pID'].values

        print("Group:%s; Experimenters: %s"%(whichCohort,dfReactionTimes['Experimenters'].values[0]))
        print("Selected pIDs",pIDs)
    saccadeRatesIllusion=[]
    saccadeRatesControl=[]
    meanReactionTime,stdReactionTime=1e3*np.median(dfReactionTimes['medianReactionTime'].values),1e3*np.median(dfReactionTimes['stdReactionTime'].values)

    for i in range(0,len(pIDs)):
        nTransI,taxis,sRateI=transitionLockedMicroSaccadeRate(pIDs[i],isControlBlock=False,
                                                              maxAmp=maxAmp,
                                                              maxVelocity=maxVelocity,
                                                              minInterSaccadicIntervalInMs=minInterSaccadicIntervalInMs,
                                                              binTrialInMs=binTrialInMs,
                                                              smoothWindwInMs=smoothWindwInMs,
                                                              timeAxisRange=timeAxisRange)
        saccadeRatesIllusion.append(sRateI)
        nTransC,taxis,sRateC=transitionLockedMicroSaccadeRate(pIDs[i],isControlBlock=True,
                                                              maxAmp=maxAmp,
                                                              maxVelocity=maxVelocity,
                                                              minInterSaccadicIntervalInMs=minInterSaccadicIntervalInMs,
                                                              binTrialInMs=binTrialInMs,
                                                              smoothWindwInMs=smoothWindwInMs,
                                                              timeAxisRange=timeAxisRange)
        saccadeRatesControl.append(sRateC)
      

    saccadeRatesIllusion=np.vstack(saccadeRatesIllusion)
    saccadeRatesControl=np.vstack(saccadeRatesControl)

    #compute mean and standard errors on means
    meanIllusion=np.mean(saccadeRatesIllusion,axis=0)
    semIllusion=np.std(saccadeRatesIllusion,axis=0)/np.sqrt(len(pIDs))
    meanControl=np.mean(saccadeRatesControl,axis=0)
    semControl=np.std(saccadeRatesControl,axis=0)/np.sqrt(len(pIDs))

    #compute significant time bins. getSignificantMask is a function in helperFunctions.py
    significantMask=getSignificantMask(seriesA=saccadeRatesControl,
                                       seriesB=saccadeRatesIllusion,
                                       pvalThresh=0.05)
    
    significantTimePoints=taxis[significantMask]



    #generate plot
    plt.title("Group: %s; nSubjects:%d"%(whichCohort,len(pIDs)))   

    plt.plot(taxis,meanIllusion,label='illusion block')
    plt.plot(taxis,meanControl,label='control block')
    plt.axvline(-meanReactionTime,ls='--',c='gray')
    plt.axvspan(-meanReactionTime-stdReactionTime,-meanReactionTime+stdReactionTime,fc='gray',alpha=0.3)
    
    plt.fill_between(taxis,y1=meanControl-semControl,
                     y2=meanControl+semControl,fc='C1',alpha=0.5)
    plt.fill_between(taxis,y1=meanIllusion-semIllusion,
                     y2=meanIllusion+semIllusion,fc='C0',alpha=0.5)
    
    if(whichCohort=='full'):        
        plt.scatter(significantTimePoints,np.ones(len(significantTimePoints))*0.7,c='C3',marker='|',zorder=1000)
        plt.text(np.mean(significantTimePoints),0.72,"*" )
    
    plt.xlim((-4000,2000))
    plt.xlabel("Time from reported transition (ms)")
    plt.ylabel("microsaccade saccade rate (rel. baseline)")
    plt.axhline(0,ls='--',color='black')  
    plt.axvline(0,ls='--',color='black') 
    plt.legend()
    plt.savefig("figures/microsaccadeRate/Group-%s_microsaccadeRate.png"%whichCohort,bbox_inches='tight',dpi=300)
    plt.clf()
    plt.close()



