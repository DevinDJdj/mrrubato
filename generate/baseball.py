
#for now each time the ball is struck will have a sound. 
#Time represents time.  
#Ball strikes are tones based on location of the ball.  
#and relative sequence is the result of the strike.  
#2016 data.  
#bq extract --destination_format CSV --compression GZIP --print_header=true bigquery-public-data:baseball.games_post_wide gs://*.appspot.com/data/mlb_games_post_wide
#bq extract --destination_format CSV --compression GZIP --print_header=true bigquery-public-data:baseball.games_wide gs://*.appspot.com/data/mlb_games_wide-*.csv
#bq extract --destination_format CSV --compression GZIP --print_header=true bigquery-public-data:baseball.schedules gs://*.appspot.com/data/schedules
#testing/data/mlb/games_wide_test.csv
#make pandas datatable.  
#sort by time
#get GPS coords by team.  
#home team shift is between 0 and 30.  
#away team shift is away team stadium location.  
#each game is a track.  
#batterposition - ball strike location - base - results
#first base (6,8,6) - hit to second (-2,0,-2) - out (-9,-6,-9)
#catcher (1,-1,1) - hit to right field (6,7,6) - single (1,6,1)
#dh (10,8,10) - hit to left field (-6,-7,-6) - double (6,-2,6)
#right field (6,7,6) - hit to left field (-6,-7,-6) - foul (-7,-8,-7)

#events
#add language baseball (1,6,-2,-6)

#walk (1,5,1)
#hit (1,6,1)
#double (6,-2,6)
#triple (-2,-6,-2)
#home run (1,6,-6,1)
#strike out (-9,1,-9)
#ground out (-9,-6,-9)
#fly out (-9,-2, -9)
#line out (-9,-2,-9)
#pop out (-9,-2,-9)
#hit by pitch (1,7,1)
#fielders choice (-9,-6,-9)
#sacrifice bunt (1,2,3)
#sacrifice fly (1,3,5)
#foul tip (-7,-8,-7)
#double play (-9,-11,-9)
#foul (-7,-10,-7) (will be by far the most used sequence I guess)
#dirt ball (1,2,1)
#run scored (1,-6,1)
#sequence will be squished into the time until the next event minus 15 seconds.  

#bases
#first (6,8,6)
#second (-2,0,-2)
#third (-6,-4,-6)
#home (1,3,1)
#catcher (1,-1,1)
#pitcher (3,1,3)
#dh (10,8,10)
#left field (-6,-7,-6)
#right field (6,7,6)
#center field (-2,-4,-2)
#short stop (-4,-6,-4)


#each game will be a track.  
#each team will have an identifier.  
#each position will have an identifier.  

#header
#team - team
#inning

#position - ball strike location - base - results
#no steals for now.  

import pandas as pd
import numpy as np
import math
import mido
from datetime import date, timedelta
import random
from mido import Message, MidiFile, MidiTrack
import requests
from datetime import datetime


instruments = {

}

previnst = [0,0,0,0,0,0,0,0,0,0]
currentinst = [0,0,0,0,0,0,0,0,0,0]
instcount = 0

prevtime = [0,0,0,0,0,0,0,0,0,0]


#df = pd.read_csv('c:/devinpiano/testing/data/mlb/games_wide_test.csv')
df = pd.read_csv('c:/devinpiano/testing/data/mlb/games_wide.csv')

df_schedule = pd.read_csv('c:/devinpiano/testing/data/mlb/schedules.csv')


print(df.head())
final_df = df.sort_values(by=['createdAt'], ascending=True)
print(final_df.head())
filtered_df = final_df[['gameId', 'createdAt', 'homeTeamId', 'homeTeamName', 'awayTeamId', 'awayTeamName', 'venueName', 'venueCity', 'venueState', 'inningNumber', 'pitcherPitchCount', 'startingBalls', 'startingStrikes', 'startingOuts', 'hitterId', 'awayBatter1', 'awayBatter2', 'awayBatter3', 'awayBatter4', 'awayBatter5', 'awayBatter6', 'awayBatter7', 'awayBatter8', 'awayBatter9', 'homeBatter1', 'homeBatter2', 'homeBatter3', 'homeBatter4', 'homeBatter5', 'homeBatter6', 'homeBatter7', 'homeBatter8', 'homeBatter9']]
print(filtered_df.head())
filtered_df2 = final_df[['gameId', 'createdAt', 'atBatEventType', 'description', 'outcomeId', 'outcomeDescription', 'hitterId', 'hitterLastName', 'hitterFirstName', 'pitcherId', 'pitcherFirstName', 'pitcherLastName', 'pitchTypeDescription', 'pitchSpeed', 'pitchZone', 'hitLocation', 'hitType', 'rob0_start', 'rob0_end', 'rob0_isOut', 'rob0_outcomeId', 'rob0_outcomeDescription', 'rob1_start', 'rob1_end', 'rob1_isOut', 'rob1_outcomeId', 'rob1_outcomeDescription', 'rob2_start', 'rob2_end', 'rob2_isOut', 'rob2_outcomeId', 'rob2_outcomeDescription', 'rob3_start', 'rob3_end', 'rob3_isOut', 'rob3_outcomeId', 'rob3_outcomeDescription']]
print(filtered_df2.head())
#homeTeamId, homeTeamName, awayTeamId, awayTeamName, venueCity, inningNumber, pitcherPitchCount, startingBalls, startingStrikes, startingOuts, 
#createdAt, description, outcomeId, outcomeDescription, hitterId, hitterLastName, hitterFirstName, pitcherId, pitcherFirstName, pitcherLastName, pitchTypeDescription, pitchSpeed, pitchZone, hitLocation, hitType
#awayBatter1

mindate = filtered_df2.iloc[0]['createdAt']
maxdate = filtered_df2.iloc[-1]['createdAt']

for i in range(10):
    stra = mindate[:-4]
    prevtime[i] = datetime.strptime(stra, '%Y-%m-%d %H:%M:%S')

timemap = [0]*60*24

for index, row in df_schedule.iterrows():
    datetime_str = row['startTime'][:-4]

    duration = row['duration_minutes']
    datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    startmins = datetime_object.hour*60 + datetime_object.minute
    for i in range(duration):
        if (startmins + i >= 60*24):
            startmins = startmins - 60*24
        timemap[startmins + i] += 1

print(timemap)    

windowstart = 0
windowend = 0
for i in range(60*24):
    if (timemap[i] == 0):
        if (windowstart == 0):
            windowstart = i
    else:
        if (windowstart !=0 and windowend == 0):
            windowend = i
        
print(windowstart)
print(windowend)


venueMap = {'Chase Field': -112.0669444, 
            'Turner Field': -84.38944444,
            'Oriole Park at Camden Yards': -76.62166667,
            'Fenway Park': -71.0975,
            'Wrigley Field': -87.65555556,
            'U.S. Cellular Field': -87.63388889,
            'Great American Ball Park': -84.50666667,
            'Progressive Field': -81.68527778,
            'Coors Field': -104.9941667,
            'Comerica Park': -83.04861111,
            'Minute Maid Park': -95.35555556,
            'Kauffman Stadium': -94.48055556,
            'Angel Stadium of Anaheim': -117.8827778,
            'Dodger Stadium': -118.24,
            'Marlins Park': -80.21972222,
            'Miller Park': -87.97111111,
            'Target Field': -93.27833333,
            'Citi Field': -73.84583333,
            'Yankee Stadium': -73.92638889,
            'O.co Coliseum': -122.2005556,
            'Oakland Coliseum': -122.2005556,
            'Citizens Bank Park': -75.16638889,
            'PNC Park': -80.00583333,
            'Petco Park': -117.1565998,
            'PETCO Park': -117.1565998,
            'Safeco Field': -122.3325,
            'AT&T Park': -122.3894444,
            'Busch Stadium': -90.19305556,
            'Tropicana Field': -82.65333333,
            'Rangers Ballpark in Arlington': -97.08277778,
            'Globe Life Park in Arlington': -97.08277778,
            'Rogers Centre': -79.38916667,
            'Nationals Park': -77.0075
            }

global teamShift
teamShift = {}


positionMap = {'pitcher': 0, 
               'catcher': 1,
               'first base': 2,
               'second base': 3,
               'third base': 4,
               'shortstop': 5,
               'left field': 6,
               'center field': 7,
                'right field': 8,
                'dh': 9
                }



venueMap = dict(sorted(venueMap.items(), key=lambda item: item[1]))
print(venueMap)
print(list(venueMap).index('Chase Field')) #shift for home team.  

venueDF = filtered_df[['homeTeamName', 'venueName', 'venueCity', 'venueState']]
venueDF.drop_duplicates(inplace=True)
for (index, row) in venueDF.iterrows():
    if (row['homeTeamName'] not in teamShift.keys()):
        print(list(venueMap).index(row['venueName']))
        print(row['venueName'])
        teamShift[row['homeTeamName']] = list(venueMap).index(row['venueName'])


print(teamShift)

"""
for index, row in venueDF.iterrows():
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + row['venueCity'] + row['venueState'])
    data = response.json()
    print(data)
    venueMap[row['venueName']] = data['results'][0]...
print(venueDF.head())
"""


def getVelocity(row, base=31):

    velm = 1
    return int(base*velm)

def getInstrument(row):
    global instcount
    temp = row['venueName']
    if (temp not in instruments.keys()):

        instcount = instcount + 1
        instruments[temp] = instcount
        rando1 = random.randint(0,60)
        rando2 = random.randint(0,60)
        if (rando1 + rando2 < 60):
            rando = 60 + rando1 + rando2    
        else:
            rando = math.abs(rando1 - rando2)
        instruments[temp] = rando
    return instruments[temp]

def getTime(row, track, orig_time = 5): #use 120 so we are divisible by 2,3,4,5
    global windowstart, windowend
    mytime = datetime.strptime(row['createdAt'], '%Y-%m-%d %H:%M:%S UTC')

    numseconds = 0
    if (mytime.hour*60 + mytime.minute > windowend and prevtime[track].hour*60 + prevtime[track].minute < windowstart):
        #new day add time until 
        #add time between prevdate and windowstart + mytime - windowend
        numseconds = windowstart*60  - windowend*60 - prevtime[track].hour*60*60 - prevtime[track].minute*60 + prevtime[track].second + mytime.hour*60*60 + mytime.minute*60 +mytime.second
        #add time for this interval
    else:
            
        numseconds = mytime.hour*60*60 + mytime.minute*60+mytime.second - prevtime[track].hour*60*60 - prevtime[track].minute*60 - prevtime[track].second
        #possible there is millisecond hits etc.  

    if (mytime.day != prevtime[track].day):
        numseconds += 24*60*60
    if (numseconds < 0):
        print(row)
        print(prevtime[track])
        print(mytime)
        print(numseconds)
        print(windowstart)
        print(windowend)
        print("Time Error")
    prevtime[track] = mytime
    return numseconds*orig_time

def getShift(row, away=False):
    if (away):
        if (row['awayTeamName'] not in teamShift.keys()):
            return 0
        shift = teamShift[row['awayTeamName']]
    else:
        if (row['homeTeamName'] not in teamShift.keys()):
            return 0
        shift = teamShift[row['homeTeamName']]

    shift -= shift%2
    return shift




def getBatterId(row):
    hitterid = row['hitterId']
    for i in range(1, 10):
        if (row['homeBatter' + str(i)] == hitterid):
            return i, False
        elif (row['awayBatter' + str(i)] == hitterid):
            return i, True
    print(row['createdAt'])
    print("Batter Error")
    return 0, False

def getNotesFromEvent(row, baserow):
    if (row['outcomeDescription'] == 'Ball' and baserow['startingBalls'] == 3):
        return [1,5,1]
    elif (row['outcomeDescription'] == 'Hit by pitch'):
        return [1,7,1]
    elif (row['outcomeDescription'] == 'Strike Looking' and baserow['startingStrikes'] == 2):
        return []
    elif (row['outcomeDescription'] == 'Strike Swinging' and baserow['startingStrikes'] == 2):
        return []
    elif (row['outcomeDescription'] == 'Foul'):
        return [-7,-10,-7]
    elif (row['outcomeDescription'] == 'Single'):
        return [1,6,1]
    elif (row['outcomeDescription'] == 'Dirt Ball'):
        return [1,2,1]
    elif (row['outcomeDescription'] == 'Double'):
        return [6,-2,6]
    elif (row['outcomeDescription'] == 'Triple'):
        return [-2,-6,-2]
    elif (row['outcomeDescription'] == 'Homerun'):
        return [1,6,-6,1]
    elif (row['outcomeDescription'] == 'Foul Tip' and baserow['startingStrikes'] == 2):
        return [-9,1,-9]
    elif (row['outcomeDescription'] == 'Foul Tip'):
        return [-7,-8,-7]
    elif (row['outcomeDescription'] == 'Strikeout'):
        return [-9,1,-9]
    elif (row['outcomeDescription'] == 'Ground Out'):
        return [-9,-6,-9]
    elif (row['outcomeDescription'] == 'Fielders Choice'):
        return [-9,-6,-9]
    elif (row['outcomeDescription'] == 'Fly Out'):
        return [-9,-2,-9]
    elif (row['outcomeDescription'] == 'Line Out'):
        return [-9,-2,-9]
    elif (row['outcomeDescription'] == 'Pop Out'):
        return [-9,-2,-9]
    elif (row['outcomeDescription'] == 'Double Play'):
        return [-9,-11,-9] 
    elif (row['outcomeDescription'] == 'Sacrifice Bunt'):
        return [1,2,3]
    elif (row['outcomeDescription'] == 'Sacrifice Fly'):
        return [1,3,5]
    elif (row['outcomeDescription'] == 'Run Scored'):
        return [1,-6,1]   
    elif (row['outcomeDescription'] == 'Double Play'):
        return [-9,-11,-9]

    return []

def getNotesFromRuns(row):
    ret = []
    for i in range(0, 4):
        start = row['rob' + str(i) + '_start']
        if (start is not None and start != ""):
            start = i
            end = row['rob' + str(i) + '_end']
            if (end == 4):
                ret += [1,-6,1]
            elif (end == 3):
                ret +=[-6,-4,-6]
            elif (end == 2):
                ret +=[-2,0,-2]
            elif (end == 1):
                ret +=[6,8,6]

    return ret
#first (6,8,6)
#second (-2,0,-2)
#third (-6,-4,-6)



    

def addNotes(row, baserow, trackid, numseconds, myvel, shift, mid):
    basenote = 60 + shift
    events = getNotesFromEvent(row, baserow)
    runs = getNotesFromRuns(row)
    track = mid.tracks[trackid]
    totalmessageseconds = 600
    messageseconds = math.floor(totalmessageseconds/(len(events)+len(runs)+4))
    #message length 120 seconds
    #playing just before the event actually takes place.  
    if (numseconds < totalmessageseconds*2):
        #problem here.  
        messageseconds = math.floor(numseconds/(len(events)+len(runs)+4))
        tempvel = math.floor(myvel/2)
        track.append(Message('note_on', note=basenote, velocity=tempvel, time=messageseconds*2))
        track.append(Message('note_off', note=basenote, velocity=127, time=messageseconds*2))
    else:
        tempvel = math.floor(myvel/4)
        track.append(Message('note_on', note=basenote, velocity=tempvel, time=numseconds-totalmessageseconds))
        track.append(Message('note_off', note=basenote, velocity=127, time=messageseconds*4))
    #this is actually the time between previous and now.  We want this to be static.  But what is the average time between?  
    for i in events:
        track.append(Message('note_on', note=basenote + i, velocity=myvel, time=messageseconds))
        track.append(Message('note_off', note=basenote + i, velocity=127, time=messageseconds))
    for i in runs:
        track.append(Message('note_on', note=basenote + i, velocity=myvel*2, time=messageseconds))
        track.append(Message('note_off', note=basenote + i, velocity=127, time=messageseconds))
                     

mid = MidiFile()

programs = []
numtracks = 10 #number of positions.  
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


trackcnt = 32
#each team has a track for now.  
#perhaps want to do something with the position of the player with hit sound.  

for index, row in filtered_df.iterrows():
    gameId = row['gameId']
    createdAt = row['createdAt']
#    row2 = filtered_df2[(filtered_df2['gameId'] == gameId) & (filtered_df2['createdAt'] == createdAt)]
#    row2 = row2.iloc[0]
    row2 = filtered_df2.loc[index]
#    print(row2)
    if (row2['atBatEventType'] == 'STEAL'):
        continue
    if (row2['atBatEventType'] == 'PITCH'):

        #trackid = batterid for now
        batterid, away = getBatterId(row)
        if (batterid ==0):
            continue
        trackid = batterid
        #team key shift 0 - 32, guess 16 is 60.  
        shift = getShift(row, away)


        trackcnt = batterid
        
        track = mid.tracks[trackid]

        numseconds = getTime(row2, trackid) #how do we sync up the time, use time since last event.  

        myvel = getVelocity(row2)

        currentinst = getInstrument(row)
        if (currentinst != previnst):
            track.append(Message('program_change', program=currentinst, time=0))
            previnst = currentinst
#            print('new instrument ' + str(currentinst))
#            print(instruments)


        addNotes(row2, row, trackid, numseconds, myvel, shift, mid)
#        if index%10000 == 0:
#            print(str(index) + " records complete")
#            print(row2)

    else:
        #delay for average time if day off.  
        myvel = 0
        basenote = 60


mid.save('baseball4.mid')
