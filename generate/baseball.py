
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
#out (-9,-6,-9)
#double play (-9,-11,-9)
#foul (-7,-8,-7) (will be by far the most used sequence I guess)
#
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


import pandas as pd
import requests

#df = pd.read_csv('c:/devinpiano/testing/data/mlb/games_wide_test.csv')
df = pd.read_csv('c:/devinpiano/testing/data/mlb/games_wide.csv')


print(df.head())
final_df = df.sort_values(by=['createdAt'], ascending=True)
print(final_df.head())
filtered_df = final_df[['homeTeamId', 'homeTeamName', 'awayTeamId', 'awayTeamName', 'venueName', 'venueCity', 'venueState', 'inningNumber', 'pitcherPitchCount', 'startingBalls', 'startingStrikes', 'startingOuts']]
print(filtered_df.head())
filtered_df2 = final_df[['createdAt', 'description', 'outcomeId', 'outcomeDescription', 'hitterId', 'hitterLastName', 'hitterFirstName', 'pitcherId', 'pitcherFirstName', 'pitcherLastName', 'pitchTypeDescription', 'pitchSpeed', 'pitchZone', 'hitLocation', 'hitType']]
print(filtered_df2.head())
#homeTeamId, homeTeamName, awayTeamId, awayTeamName, venueCity, inningNumber, pitcherPitchCount, startingBalls, startingStrikes, startingOuts, 
#createdAt, description, outcomeId, outcomeDescription, hitterId, hitterLastName, hitterFirstName, pitcherId, pitcherFirstName, pitcherLastName, pitchTypeDescription, pitchSpeed, pitchZone, hitLocation, hitType

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

teamShift = {}

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

