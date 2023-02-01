#from test.csv, generate an html page which has graphs etc.  
#Generate a page for each song which shows each iteration
#Date/Time -> speed
#link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
#for now just generate a csv file.  
#dont download the videos, just get the written description


#notesplayed

#need written words to explain actually what I am doing.  
#category "BOOK" or "PLAY" or something for not in-time thoughts, but more refined words.  
#each subdivision can be "CHAPTER" or "ACT"
#how can I write a book in real time?  
#how can I construct this so that I am not repeating myself?  
#BOOK will be written in parts, representing each thought period, and included in github.  
#it will explain the past period, while playing music tied to the next period and explaining current thought on next period.  
#for now get rid of the categories, this is cumbersome to do.  
#just have WORDS, BOOK, COMPOSITION, MEMORY, HANASHI, HON
#other labels like SIGHTREAD, or BESTOFDAY just put into description.  
#lets translate the book to Japanese as well, kind of annoying, but it will improve my Japanese singing so probably worth it.  

#represent communication types etc with different intervals and different pitch variations.  
#must have pitch change be the differentiator, not true pitch.  
#the same musical representation can be mapped to a computer representation as well.  
#this can serve as a shared language probably with some thought.  

#

import sys
 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/')
 
 
import cred
import pandas as pd
import requests
import json

def get_duration(d):
    end_minute_sec = d['endtime'].split(":")
    start_minute_sec = d['starttime'].split(":")
    duration = -1
    try:
        print(d['endtime'])
        duration = (int(end_minute_sec[0]) - int(start_minute_sec[0]))*60
        print(duration)
        duration += (int(end_minute_sec[1]) - int(start_minute_sec[1]))
        print(duration)
        d['duration'] = duration
    except:
        d['duration'] = None
    if duration < 0:
        duration = None
    return duration
#print(cred.APIKEY)



    #link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
df = pd.read_csv("test.csv",parse_dates=['PublishedDate'])
from datetime import time
import datetime
#time1 = datetime.time(13,27,45,4600)
#print(time1)

df['duration'] = df.apply(get_duration, axis=1)

#print(df.groupby('Title')[['duration']].mean())

import codecs
import sys 
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
fig = plt.figure()
plt.figure().clear()
plt.close('all')
plt.cla()
plt.clf()

import japanize


    
df.groupby('Title')[['duration']].mean().to_csv("by_title.csv")
#plt.figure()

#df['duration'].plot(kind="bar")
#df.groupby('Title')[['duration']].mean().sort_values(by=['Title']).plot()
#plt.show()

df[['Title', 'duration']].sort_values(by=['Title']).plot(subplots=True)

f = open("analyze2.txt", "w",encoding='utf-8')

#df[['Title', 'duration']].sort_values(by=['Title']).plot(subplots=True)
#df.plot(x='PublishedDate', y='duration', subplots=True)
#plt.show()

a = 0
titles = df["Title"].unique()
list_no_case = {v.lower(): v for v in titles}.values()

gothicfont = {'fontname':'MS Gothic'}

date_time = ["2022-06-01", "2022-08-01", "2022-10-01", "2022-12-01", "2023-02-01"]
date_time = pd.to_datetime(date_time)
plt.rcParams['figure.figsize'] = [12, 4]

for t in list_no_case:
    tempdf = df.loc[(df['Title'] == t)].sort_values(by=['PublishedDate','iteration'])
    #sum of the time here.  
    
#    plt.xlabel('PublishedDate')
#    plt.ylabel('duration')
#    plt.title(t)
#    ttempdf = tempdf#.loc[tempdf['iteration']==1]


    
    f.write(t)
    f.write(str(tempdf.size))
    
    
    plt.xticks(rotation=90)
    plt.title(t, **gothicfont)
    plt.tight_layout()

    ax = tempdf.plot(x='PublishedDate', y='duration', title=t, marker='o')
    ax.set_xlim(xmin=datetime.date(2022, 6, 30), xmax=datetime.date(2022, 12, 31))
    
    plt.savefig('./output/test/analyze/' + str(a) + '.png')
    a += 1
    plt.clf()
    
#s = pd.Series([1, 2, 3])
#fig, ax = plt.subplots()
#s.plot.bar()
#fig.savefig('my_plot.png')


#want to also just have simple stats about number of times played etc.  
#amount of time playing a particular song.  
#that is about all we are going to get from this.  
#analyzing the times is not going to work with such inaccurate data this year#2.  
#this should work next year.  

