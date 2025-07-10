import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def getReactionTimes():
    #load list of valid participants
    dfSubj=pd.read_csv("./datafiles/EMPRA.csv")
    dfSubj=dfSubj[dfSubj['Include participant?']=='Y'].reset_index(drop=True)

    for iSubj in range(len(dfSubj)):
        #load trigger information
        dfTriggers=pd.read_csv("./datafiles/triggerInfo/task_Enigma_%s_s1_Triggers.csv"%(dfSubj.loc[iSubj,'pID']))

        #remove practice block
        dfTriggers=dfTriggers[np.logical_not(dfTriggers['blockID']=='pract')].reset_index(drop=True)
        dfTriggers['blockID']=dfTriggers['blockID'].values.astype("int")

        #select control blocks
        dfTriggers=dfTriggers[dfTriggers['blockID']>=4].reset_index(drop=True)
        #find number of transitions
        nFlips=np.sum(np.logical_or(dfTriggers['triggerName']=='startStimulusRotation_Left',dfTriggers['triggerName']=='startStimulusRotation_Right'))
        
        #initialize empty arrays to store relevent info
        reactionTime=np.zeros(nFlips)+np.nan
        blockID=np.zeros(nFlips)
        isCorrect=np.zeros(nFlips)


        iTrans=0

        #loop over all triggers
        for i in range(0,len(dfTriggers)-1):
            trigCurrent=dfTriggers.loc[i,'triggerName']
            trigNext=dfTriggers.loc[i+1,'triggerName']
            
            timeDiffToNext=dfTriggers.loc[i+1,'timestamp_psyc']-dfTriggers.loc[i,'timestamp_psyc']
            #if rotation was anti-clockwise
            if(trigCurrent=='startStimulusRotation_Left'):
                blockID[iTrans]=dfTriggers.loc[i,'blockID']
                if(trigNext=='keyPress_Left'):
                    isCorrect[iTrans]=True
                    reactionTime[iTrans]=timeDiffToNext
                elif(trigNext=='keyPress_Right'):
                    isCorrect[iTrans]=False
                    reactionTime[iTrans]=timeDiffToNext
                iTrans+=1
            #if rotation was clockwise
            elif(trigCurrent=='startStimulusRotation_Right'):
                blockID[iTrans]=dfTriggers.loc[i,'blockID']
                if(trigNext=='keyPress_Right'):
                    isCorrect[iTrans]=True
                    reactionTime[iTrans]=timeDiffToNext
                elif(trigNext=='keyPress_Left'):
                    isCorrect[iTrans]=False
                    reactionTime[iTrans]=timeDiffToNext
                iTrans+=1
        nanMask=np.logical_not(np.isnan(reactionTime))
        #get relevent means/std/medians
        dfSubj.loc[iSubj,'correctFraction']=np.mean(isCorrect[nanMask])
        dfSubj.loc[iSubj,'meanReactionTime']=np.mean(reactionTime[nanMask])
        dfSubj.loc[iSubj,'stdReactionTime']=np.std(reactionTime[nanMask])
        dfSubj.loc[iSubj,'medianReactionTime']=np.median(reactionTime[nanMask])
    #save to csv file
    dfSubj.to_csv("./datafiles/reactionTimes.csv")
    #print(dfTransitions)
       
        
getReactionTimes()