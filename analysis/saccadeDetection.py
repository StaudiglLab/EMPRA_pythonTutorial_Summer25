import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from helperFunctions import *

def getAboveThresholdPoints(velocity,threshold):
    #computation of a robust metric of deviation, following Engbert et al. 2003
    deviation=np.sqrt(np.nanmedian(velocity**2)-np.nanmedian(velocity)**2)
    maskDet=np.abs(velocity)>threshold*deviation
    return maskDet

def detectSaccadesCore(ts, #time axis
                       X_pos_L,X_pos_R, #x-coordinates of left and right eye
                       Y_pos_L,Y_pos_R, #y-coordinates of left and right eye
                       thresholdVel=6,  #threshold for detection of saccades
                       minDurationInSamples=6  #minimum duration of any detected events to qualify as a saccade
                       ):
    

    #computer velocities

    X_vel_L=getVelocity(X_pos_L)/(ts[1]-ts[0]) #compute velocity along X-axis for left eye
    X_vel_R=getVelocity(X_pos_R)/(ts[1]-ts[0]) #compute velocity along X-axis for right eye
    Y_vel_L=getVelocity(Y_pos_L)/(ts[1]-ts[0]) #compute velocity along Y-axis for left eye
    Y_vel_R=getVelocity(Y_pos_R)/(ts[1]-ts[0]) #compute velocity along Y-axis for right eye

    #compute magnitude of velocity for each eye
    speed_L=np.sqrt(X_vel_L**2+Y_vel_L**2) #speed for left eye
    speed_R=np.sqrt(X_vel_R**2+Y_vel_R**2) #speed for right eye

    #compute average speed of the two eyes
    speed=(speed_L+speed_R)/2.
   
    #get masks corresponding to points that meets velocity threshold
    maskDet_X_L=getAboveThresholdPoints(X_vel_L,thresholdVel)
    maskDet_X_R=getAboveThresholdPoints(X_vel_R,thresholdVel)
    maskDet_Y_L=getAboveThresholdPoints(Y_vel_L,thresholdVel)
    maskDet_Y_R=getAboveThresholdPoints(Y_vel_R,thresholdVel)

    #final detection mask, following Engbert et al. 2003, saccades are defined as binocular events
    #i.e. should be above threshold for both L AND R eye 
    #in either the X or Y direction

    maskDet_X=np.logical_and(maskDet_X_L,maskDet_X_R) 
    maskDet_Y=np.logical_and(maskDet_Y_L,maskDet_Y_R) 

    maskDet=np.logical_or(maskDet_X,maskDet_Y)
    
    #get the start index and width corresponding to each detection
    #use helper function in file helperFunctions.py for this
    startIndx,widthIndx=getClustersFromMask(maskDet)

    #selecting only those saccades that have a minimum specified duration
    selmask=widthIndx>minDurationInSamples
    startIndx,widthIndx=startIndx[selmask],widthIndx[selmask]

    #get amplitude of saccades for each direction and each eye

    saccadeAmplitude_X_L=X_pos_L[startIndx]-X_pos_L[startIndx+widthIndx-1]
    saccadeAmplitude_Y_L=Y_pos_L[startIndx]-Y_pos_L[startIndx+widthIndx-1]

    saccadeAmplitude_X_R=X_pos_R[startIndx]-X_pos_R[startIndx+widthIndx-1]
    saccadeAmplitude_Y_R=Y_pos_R[startIndx]-Y_pos_R[startIndx+widthIndx-1]

    amplitude_L=np.sqrt(saccadeAmplitude_X_L**2+saccadeAmplitude_Y_L**2)
    amplitude_R=np.sqrt(saccadeAmplitude_X_R**2+saccadeAmplitude_Y_R**2)

    amplitude=(amplitude_L+amplitude_R)/2.
    saccadeAngle=np.degrees(np.arctan2((saccadeAmplitude_Y_L+saccadeAmplitude_Y_R)/2.,(saccadeAmplitude_X_L+saccadeAmplitude_X_R)/2.))



    #for each saccade,get peak speed (i.e. amplitude of velocity) 
    peakSpeedIndx=np.zeros_like(startIndx)
    for j in range(0,len(startIndx)):
        peakSpeedIndx[j]=startIndx[j]+np.argmax(speed[startIndx[j]:startIndx[j]+widthIndx[j]-1])


    #write saccade parameters to a file
    dfSaccades=pd.DataFrame()
    dfSaccades['startTime']=ts[startIndx]
    dfSaccades['peakVelocityTime']=ts[peakSpeedIndx]
    dfSaccades['stopTime']=ts[startIndx+widthIndx-1]
    dfSaccades['amplitude']=amplitude
    dfSaccades['angle']=saccadeAngle
    dfSaccades['peakVelocity']=speed[peakSpeedIndx] 
    

    '''
    selmask=dfSaccades['peakVelocity']<60*dfSaccades['amplitude']
    if(np.sum(selmask)>0):
        print(dfSaccades[selmask])
        print(dfSaccades.loc[np.arange(len(dfSaccades))[selmask]-1])
        fig,axs=plt.subplots(2,1,sharex=True)
        axs[0].plot(ts,X_pos_L)
        axs[0].plot(ts,Y_pos_L)
        axs[1].plot(ts,X_vel_L)
        axs[1].plot(ts,Y_vel_L)
        for i in range(0,len(peakSpeedIndx[selmask])):
            axs[1].axvline(ts[peakSpeedIndx[selmask][i]])
            axs[0].axvline(ts[peakSpeedIndx[selmask][i]])
        plt.show()
    '''
    return dfSaccades


def detectSaccades(pID,
                   rawdatadirectory,
                   nBlocks=8,           #number of blocks
                   screenHeight=298.89, #height of screen, in mm
                   screenWidth=531.36,  #width of screen, in mm
                   screenDistance=800,  #distance of eye to screen, in mm
                   nanExpandInMs=40,     #amount of time around each NaN (blinks, usually) that are marked as invalid
                   thresholdVel=6,  #threshold for detection of saccades
                   minDurationInSamples=6  #minimum duration of any detected events to qualify as a saccade
                       
                   ):
    dfSaccades=[]

    #reading the trigger log to figure out the start time for each block
    dfTriggers=pd.read_csv(rawdatadirectory+"/%s_s1_enigma/task_Enigma_%s_s1_Triggers.csv"%(pID,pID))
    dfTriggers=dfTriggers[np.logical_and(dfTriggers['triggerName']=='stimulusDisplayStart',np.logical_not(dfTriggers['blockID']=='pract'))].reset_index(drop=True)
    dfTriggers['blockID']=dfTriggers['blockID'].values.astype("int")
    
    #iterating over all blocks of the experiment
    for block in range(0,nBlocks):
        #start timestamp of the block from the trigger log
        tsStartBlock=dfTriggers['timestamp_tobii'][dfTriggers['blockID']==block].values[0]/1e6

        #read eyetracker raw data
        df=pd.read_hdf(rawdatadirectory+"/%s_s1_enigma/task_Enigma_%s_s1_Tobii_%02d.h5"%(pID,pID,block))
        ts=df['system_time_stamp'].values/1e6 

        df=df[ts>tsStartBlock]  #this ensures the calibration period is excluded from the data
        ts=ts[ts>tsStartBlock]

        #convert from normalized coordinates to dva
        right_x=np.degrees(np.arctan((df['right_gaze_point_on_display_area_x'].values-0.5)*screenWidth/screenDistance))
        left_x=np.degrees(np.arctan((df['left_gaze_point_on_display_area_x'].values-0.5)*screenWidth/screenDistance))
        left_y=np.degrees(np.arctan((df['left_gaze_point_on_display_area_y'].values-0.5)*screenHeight/screenDistance))
        right_y=np.degrees(np.arctan((df['right_gaze_point_on_display_area_y'].values-0.5)*screenHeight/screenDistance))

        #mark points around NaNs in the raw data (usually blinks) also as NaNs
        #uses helper function expandNaNs 
        right_x=expandNaNs(right_x,int(1e-3*nanExpandInMs/(ts[1]-ts[0])))
        left_x=expandNaNs(left_x,int(1e-3*nanExpandInMs/(ts[1]-ts[0])))
        left_y=expandNaNs(left_y,int(1e-3*nanExpandInMs/(ts[1]-ts[0])))
        right_y=expandNaNs(right_y,int(1e-3*nanExpandInMs/(ts[1]-ts[0])))



        dfSaccades_=detectSaccadesCore(ts=ts,X_pos_L=left_x,Y_pos_L=left_y,
                                       X_pos_R=right_x,Y_pos_R=right_y,
                                       thresholdVel=thresholdVel,
                                       minDurationInSamples=minDurationInSamples)
        
        dfSaccades.append(dfSaccades_)
    
    #concatenate all detections of saccades into a file
    pd.concat(dfSaccades).to_csv("./datafiles/saccades/task_Enigma_%s_s1_saccades.csv"%(pID))

#loop over all participants
for subID in np.arange(1,32):
    print("Running detection for Sub_%03d"%subID)
    if(subID==17):
         continue
    detectSaccades('Sub_%03d'%subID,rawdatadirectory='/media/data/chowdhury/EMPRA_enigma/data')
