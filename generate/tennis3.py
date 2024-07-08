#20240703

import pandas as pd
import numpy as np
import mido
from mido import Message, MidiFile, MidiTrack


def getTimeFromRound(rnd, orig_time = 120): #use 120 so we are divisible by 2,3,4,5
    mult = 1
    if (rnd == '1st Round'):
        mult = 1
    elif (rnd == '2nd Round'):
        mult = 1.25
    elif (rnd == '3rd Round'):
        mult = 1.5
    elif (rnd == '4th Round'):
        mult = 1.75
    elif (rnd == 'Quarterfinals'):
        mult = 2
    elif (rnd == 'Semifinals'):
        mult = 2.5
    elif (rnd == 'The Final'):
        mult = 3
    return mult*orig_time    

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

track.append(Message('program_change', program=12, time=0))
#track.append(Message('note_on', note=64, velocity=64, time=32))
#track.append(Message('note_off', note=64, velocity=127, time=32))
#track.append(Message('note_on', note=65, velocity=64, time=32))
#track.append(Message('note_off', note=65, velocity=127, time=32))


df = pd.read_csv('C:/devinpiano/testing/tennis/data/archive/atp_mens_tour/2005.csv')
print(df)

sorted_df = df.sort_values(by=['Date'], ascending=True)

for index, row in sorted_df.iterrows():
    if index==3:
        print(row)

        print(row['Date'])
        print(row['Round'])
        print(row['WRank'] / row['LRank'])
        print(row['WPts'] / row['LPts'])
        print(row['Best of'])
    if (not (np.isnan(row['Wsets'] or np.isnan(row['Lsets'])))):
        totalsets = int(row['Wsets'] + row['Lsets'])
        for x in range(1, totalsets+1):

    #        print(row['W' + str(x)])
    #        print(row['L' + str(x)])
            mytime = getTimeFromRound(row['Round'])
            mytime = int(mytime/totalsets) #each round should be same time.  

            #get base note based on WRank/LRank
            track.append(Message('note_on', note=60 + int(row['W' + str(x)]), velocity=64, time=mytime))
            track.append(Message('note_off', note=60 + int(row['W' + str(x)]), velocity=127, time=mytime))
            track.append(Message('note_on', note=60 + int(row['L' + str(x)]), velocity=64, time=mytime))
            track.append(Message('note_off', note=60 + int(row['L' + str(x)]), velocity=127, time=mytime))
        


mid.save('tennis3.mid')
