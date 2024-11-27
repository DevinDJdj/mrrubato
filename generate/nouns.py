#JUMP TO PLANE ...
#JUMP TO LOCATION ...
#3D or 2D?  
#Is this possible to visualize language in a spatial structure?  
#Should try..
#This is already what the LLMs are doing.  
#LEFT is past RIGHT is future?  South-facing...

#We should see symetry in this graph with opposite/synonym.  
#Perhaps different planes for part of speech, and Plane selection and meta functionality would be with left hand.  
#While word/location selection with right.  

#Try to keep symetry across planes with meaning structure.  
#We need a word2vec graph with 3 dimensions. 

#So we just need to generate the models the way we want.  
#Create a similarity/locality graph with only keeping certain types of speech.  
#We can probably just use random text.  
#Parse the text, keep only certain part of speech.  
#Then generate word2vec model and analyze the structure of this model.  


import gensim.models as g
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import nltk
from nltk.tokenize import word_tokenize
import os
import spacy
from collections import Counter

#nlp = spacy.load("en_core_web_sm")


nltk.download('punkt')
#nltk.download()

is_noun = lambda pos: pos[:2] == 'NN'

lines = 'You can never plan the future by the past.  But you can learn about the present from the past. And you can plan for the future in the present.  '
#why JJ instead of NN?  'past', 'present', 'present'
#not significant at the moment.  


lines = lines.lower()
tokenized = nltk.word_tokenize(lines)
nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]

#https://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk
for (word, pos) in nltk.pos_tag(tokenized):
    print(word, pos)

print(nouns) # ['future', 'past']

#create new input corpus with only nouns.  
#train the model with this corpus.  Using only 3 dimensions.  
#dims = [50, 150, 300]
#https://github.com/nickvdw/word2vec-from-scratch/blob/master/word2vec.ipynb
#then visualize resulting model with this.  
#https://stackoverflow.com/questions/43776572/visualise-word2vec-generated-from-gensim-using-t-sne
