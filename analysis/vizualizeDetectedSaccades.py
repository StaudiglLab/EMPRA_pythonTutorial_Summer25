import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from helperFunctions import *




def vizualizeDetectedSaccades(pID,blockNumber,
                   rawdatadirectory,
                   screenHeight=298.89, #height of screen, in mm
                   screenWidth=531.36,  #width of screen, in mm
                   screenDistance=800,  #distance of eye to screen, in mm
                   nanExpandInMs=40     #amount of time around each NaN (blinks, usually) that are marked as invalid
                   ):
    dfSaccades=[]

    #reading the trigger log to figure out the start time for each block
    dfTriggers=pd.read_csv(rawdatadirectory+"/%s_s1_enigma/task_Enigma_%s_s1_Triggers.csv"%(pID,pID))
    dfTriggers=dfTriggers[np.logical_and(dfTriggers['triggerName']=='stimulusDisplayStart',np.logical_not(dfTriggers['blockID']=='pract'))].reset_index(drop=True)
    dfTriggers['blockID']=dfTriggers['blockID'].values.astype("int")
    
   
    #start timestamp of the block from the trigger log
    tsStartBlock=dfTriggers['timestamp_tobii'][dfTriggers['blockID']==blockNumber-1].values[0]/1e6
    tsEndBlock=dfTriggers['timestamp_tobii'][dfTriggers['blockID']==blockNumber-1].values[-1]/1e6

    #read eyetracker raw data
    df=pd.read_hdf(rawdatadirectory+"/%s_s1_enigma/task_Enigma_%s_s1_Tobii_%02d.h5"%(pID,pID,blockNumber-1))
    ts=df['system_time_stamp'].values/1e6 

    df=df[np.logical_and(ts>tsStartBlock,ts<tsEndBlock)]  #this ensures the calibration period is excluded from the data
    ts=ts[np.logical_and(ts>tsStartBlock,ts<tsEndBlock)]

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



       
    
    #concatenate all detections of saccades into a file
    dfSaccades=pd.read_csv("./datafiles/saccades/task_Enigma_%s_s1_saccades.csv"%(pID))   
    onsetTime=dfSaccades['startTime'].values
    onsetTime=onsetTime[np.logical_and(onsetTime>tsStartBlock,onsetTime<tsEndBlock)]
    
    plt.figure(figsize=(12,4))
    plt.plot(ts,right_x,label='right x')
    plt.plot(ts,right_y,label='right y')
    plt.plot(ts,left_x,label='left x')
    plt.plot(ts,left_y,label='left y')
    plt.xlabel("Time (sec)")
    plt.ylabel("Angle (degree)")
    for i in range(0,len(onsetTime)):
        plt.axvline(onsetTime[i])
    plt.legend()
    plt.show()

vizualizeDetectedSaccades('Sub_003',5,rawdatadirectory='/home/aditya/EMPRA_enigma/data')
