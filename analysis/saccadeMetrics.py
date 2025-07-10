import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




def plotSaccadeMetric(whichCohort='full',maxAmp=2,maxVelocity=200,minInterSaccadicInterval=150):
    
    #select subjects for the particiular cohort
    dfSubj=pd.read_csv("./datafiles/EMPRA.csv")
    dfSubjValid=dfSubj[dfSubj['Include participant?']=='Y'].reset_index(drop=True)
    if(whichCohort=='full'):
        pIDs=dfSubjValid['pID'].values
        marksize=.01 #improves plot readability
    else:
        selmask=dfSubjValid['GroupID']==whichCohort
        if(np.sum(selmask)==0):
            print("No participants found. Please make sure that the group ID is correct")
            return -1
        pIDs=dfSubjValid['pID'].values[selmask]
        print("Experimenters: %s"%(dfSubjValid['Experimenters'].values[selmask][0]))
        marksize=.1 #improves plot readability

    print("Group:%s; Selected participants:"%whichCohort,pIDs)
    
    amplitudes=[]
    velocities=[]
    angles=[]

    #loop over participants and load information for detected saccades
    for pID in pIDs:
        dfSaccades=pd.read_csv("./datafiles/saccades/task_Enigma_%s_s1_saccades.csv"%(pID)).sort_values(by='startTime')   
        interSaccadicInterval=dfSaccades['startTime'].values[1:]-dfSaccades['stopTime'].values[:-1]  
        dfSaccades=dfSaccades[1:]
        dfSaccades=dfSaccades[np.logical_and.reduce((interSaccadicInterval>minInterSaccadicInterval/1e3,dfSaccades['amplitude']<maxAmp,dfSaccades['peakVelocity']<maxVelocity))]
     
        
        amplitudes=np.append(amplitudes,dfSaccades['amplitude'])
        velocities=np.append(velocities,dfSaccades['peakVelocity'])
        angles=np.append(angles,dfSaccades['angle'])
    
    #plot saccade metrics
    fig = plt.figure(figsize=(8,4))
    fig.suptitle("Group: %s; nSubjects:%d; nSaccades: %d"%(whichCohort,len(pIDs),len(amplitudes)))
    ax1 = plt.subplot(121)
    ax2 = plt.subplot(122, projection = 'polar')  
    #plot velocity of saccades vs. amplitude  
    ax1.scatter(amplitudes,velocities,s=marksize)
    ax1.set_ylabel("Velocity (deg/s)")
    ax1.set_xlabel("Amplitude (deg)")
    ax1.set_xlim((0,maxAmp))
    ax1.set_ylim((0,maxVelocity))

    #plot distribution of angles
    ax2.hist(np.radians(angles),bins=20,density=True)
    plt.savefig("figures/saccadeMetrics/Group-%s_saccadeMetrics.png"%whichCohort)
    plt.clf()
    plt.close()
