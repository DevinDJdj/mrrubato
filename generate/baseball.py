
#for now each time the ball is struck will have a sound. 
#Time represents time.  
#Ball strikes are tones based on location of the ball.  
#and relative sequence is the result of the strike.  

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
#foul (-7,-8) (will be by far the most used sequence I guess)
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

