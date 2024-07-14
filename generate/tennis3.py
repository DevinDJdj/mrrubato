#20240703

import pandas as pd
import numpy as np
import math
import mido
from datetime import date, timedelta
import random
from mido import Message, MidiFile, MidiTrack

instruments = {

}

previnst = [0,0,0,0,0,0,0,0,0]
currentinst = [0,0,0,0,0,0,0,0,0]
instcount = 0

def getVelocity(row, base=31):

    velm = 1
    if (row['Series'] == 'International'):
        velm = 1
    elif(row['Series'] == 'International Gold'):
        velm = 1.5
    elif(row['Series'] == 'Grand Slam'):
        velm = 2.5
    elif(row['Series'] == 'Masters'):
        velm = 2
    elif(row['Series'] == 'Masters Cup'):
        velm = 3

    return int(base*velm)

def getInstrument(row):
    global instcount
    temp = row['Location'] + row['Surface']
    if (temp not in instruments.keys()):

        instcount = instcount + 1
        instruments[temp] = instcount
        instruments[temp] = random.randint(0, 120)
    return instruments[temp]

def getTimeFromRound(rnd, orig_time = 120): #use 120 so we are divisible by 2,3,4,5
    mult = 1
    if (rnd == '1st Round'):
        mult = 1
    elif (rnd == '2nd Round'):
        mult = 2
    elif (rnd == '3rd Round'):
        mult = 4
    elif (rnd == '4th Round'):
        mult = 8
    elif (rnd == 'Quarterfinals'):
        mult = 16
    elif (rnd == 'Semifinals'):
        mult = 32
    elif (rnd == 'The Final'):
        mult = 64
    return mult*orig_time


def getShift(row):
    shift = abs(row['WRank'] - row['LRank'])
    sign = 1
    if (row['LRank'] > row['WRank']):
        sign = -1
    if (np.isnan(shift)):
        shift = 1
    elif(shift > math.pow(math.e, 6)):
        shift = math.pow(math.e, 6)

    shift = math.log(shift)
    shift = shift/2
    return shift*sign

def getDates(start=2005, end=2006):
    alldates = []
    start_date = date(start, 1, 1)
    end_date = date(end, 1, 1)
    delta = timedelta(days=1)
    while start_date <= end_date:
        alldates.append(start_date.strftime("%Y-%m-%d"))
#        print(start_date.strftime("%Y-%m-%d"))
        start_date += delta
    return alldates

mid = MidiFile()

programs = []
numtracks = 4
for n in range(numtracks):
    track = MidiTrack()
    programs.append(1)
    mid.tracks.append(track)


#track.append(Message('program_change', program=1, time=0))
#use this to adjust instruments based on tournament and surface.  
#track.append(Message('note_on', note=64, velocity=64, time=32))
#track.append(Message('note_off', note=64, velocity=127, time=32))
#track.append(Message('note_on', note=65, velocity=64, time=32))
#track.append(Message('note_off', note=65, velocity=127, time=32))


df = pd.read_csv('C:/devinpiano/testing/tennis/data/archive/atp_mens_tour/2005.csv')
print(df)

sorted_df = df.sort_values(by=['Date'], ascending=True)

trackcnt = 0

alldates = getDates(2005, 2006)

for d in alldates:
    mask = df['Date'] == d
    if (len(df[mask]) > 0):
        mylen = len(df[mask])

        if (trackcnt < numtracks-1):
            trackcnt = trackcnt + 1
        else:
            trackcnt = 0
        
        for index, row in df[mask].iterrows():
            if (not (np.isnan(row['Wsets'] or np.isnan(row['Lsets'])))):
                shift = getShift(row)


                totalsets = int(row['Wsets'] + row['Lsets'])
                currentinst[trackcnt] = getInstrument(row)
                if (currentinst[trackcnt] != previnst[trackcnt]):
                    track.append(Message('program_change', program=currentinst[trackcnt], time=0))
                    previnst[trackcnt] = currentinst[trackcnt]
                    print('new instrument ' + str(currentinst[trackcnt]))
                    print(instruments)
                mytime = getTimeFromRound(row['Round'])
#                trackcnt = int(math.log2(mytime/120))
#                print(mytime)
                track = mid.tracks[trackcnt]
                if (totalsets > 0):
                    mytime = int(mytime/totalsets) #each round should be same time.  
                myvel = getVelocity(row)
                for x in range(1, totalsets+1):

            #        print(row['W' + str(x)])
            #        print(row['L' + str(x)])

                    #get base note based on WRank/LRank
                    basenote = 60 + int(shift*12)

                    basenote = 60 + (int(shift*2)%7)*6


                    track.append(Message('note_on', note=basenote + int(row['W' + str(x)]), velocity=myvel, time=mytime))
                    track.append(Message('note_off', note=basenote + int(row['W' + str(x)]), velocity=127, time=mytime))
                    track.append(Message('note_on', note=basenote + int(row['L' + str(x)]), velocity=myvel, time=mytime))
                    track.append(Message('note_off', note=basenote + int(row['L' + str(x)]), velocity=127, time=mytime))

    else:
        #delay for average time if day off.  
        myvel = 0
        basenote = 60
        mytime = getTimeFromRound('')
        mytime *= len(df)/365
        mytime = int(mytime)
        track.append(Message('note_on', note=basenote, velocity=myvel, time=mytime))
        track.append(Message('note_off', note=basenote, velocity=myvel, time=mytime))
        track.append(Message('note_on', note=basenote, velocity=myvel, time=mytime))
        track.append(Message('note_off', note=basenote, velocity=myvel, time=mytime))


"""
for index, row in sorted_df.iterrows():

    if index==3:
        print(row)

        print(row['Date'])
        print(row['Round'])
        print(row['WRank'] / row['LRank'])
        print(row['WPts'] / row['LPts'])
        print(row['Best of'])
    if (not (np.isnan(row['Wsets'] or np.isnan(row['Lsets'])))):
        shift = getShift(row)


        totalsets = int(row['Wsets'] + row['Lsets'])
        currentinst = getInstrument(row)
        if (currentinst != previnst):
            track.append(Message('program_change', program=currentinst, time=0))
            previnst = currentinst
            print('new instrument ' + str(currentinst))
            print(instruments)
        mytime = getTimeFromRound(row['Round'])
        if (totalsets > 0):
            mytime = int(mytime/totalsets) #each round should be same time.  
        myvel = getVelocity(row)
        for x in range(1, totalsets+1):

    #        print(row['W' + str(x)])
    #        print(row['L' + str(x)])

            #get base note based on WRank/LRank
            basenote = 60 + int(shift*12)


            track.append(Message('note_on', note=basenote + int(row['W' + str(x)]), velocity=myvel, time=mytime))
            track.append(Message('note_off', note=basenote + int(row['W' + str(x)]), velocity=127, time=mytime))
            track.append(Message('note_on', note=basenote + int(row['L' + str(x)]), velocity=myvel, time=mytime))
            track.append(Message('note_off', note=basenote + int(row['L' + str(x)]), velocity=127, time=mytime))
        
"""

mid.save('tennis3.mid')
