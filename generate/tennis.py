#take input of tennis match audio, and use the timings which occur and separate the sounds of the 
#ball hitting the racket, the players footsteps, the type of shot, and the applause.  
#every distinct type of act should be identified and a sound timbre should be created for each.
#represent the tennis match in a midi file, and compose a piece of music based on the match.  
#Group by each player, and create a life track for each player in sequence of matches played.  
#or perhaps also create some combination of multiple matches played.  
#or by player/location etc.  
#maxsimultaneous = 4?  
#work with each player to choose ball striking sound etc.  

#test with this https://www.youtube.com/@WTA/playlists
#https://www.youtube.com/@tennistv/playlists


#https://shiqiang.wang/papers/AB_MMSports2019.pdf
#https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=888c823137434f4ebb85083bcb20f7a2ed486d36
#https://medium.com/@kosolapov.aetp/tennis-analysis-using-deep-learning-and-machine-learning-a5a74db7e2ee
#tennis ball/player detection
#https://github.com/yastrebksv/TennisProject
#https://www.youtube.com/watch?v=L23oIHZE14w
#audio event detection
#https://github.com/amsehili/auditok


###start here###
#full match playlist:
#WTA
#https://www.youtube.com/playlist?list=PLhQBpwasxUpldXpIymjy_FeQrax9qXGNT
#https://www.youtube.com/playlist?list=PL_2A0MxHOgdaYmi__7UiR8HQqkPaGdmqr

#USOPEN
#https://www.youtube.com/watch?v=HCIhFyeQxu0&list=PL_2A0MxHOgdYzDdqZaYu4nQ6jdl95rKvK
#https://www.youtube.com/watch?v=RzEw4pTdLEU&list=PL_2A0MxHOgdY7HQMncvHtHLoE4PtMBnFy
#classic matches
#https://www.youtube.com/watch?v=DCzT_AmY0HY&list=PL_2A0MxHOgdZxZ3vK104p51lFOFVsEgrR

#AUOPEN
#https://www.youtube.com/watch?v=HgN6t1-JhDs&list=PL2RR--XMozwUbAdvjCLuhe4Cuqgfv6X1U
#https://www.youtube.com/watch?v=q7b-fcV1Q-4&list=PL2RR--XMozwUKlrwbxNPUQAW-SU8AJvI_
#https://www.youtube.com/watch?v=6I06-ITW88k&list=PL2RR--XMozwUsQ8ieTUc-0VkWdKpzV4mK



#ROLAND GARROS
#no full playlist
#https://www.youtube.com/c/rolandgarros

#WIMBLEDON
#no full playlist
#https://www.youtube.com/@Wimbledon/playlists


#download all videos and create some structure for Player and location etc.  
#use audio event detection to get events.  


#pip install soundata

import soundata

dataset = soundata.initialize('urbansound8k')
dataset.download()  # download the dataset
dataset.validate()  # validate that all the expected files are there

example_clip = dataset.choice_clip()  # choose a random example clip
print(example_clip)  # see the available data
