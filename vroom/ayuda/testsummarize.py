from gensim.summarization.summarizer import summarize                  
from gensim.summarization import keywords                 
import wikipedia              
import en_core_web_sm                  


wikisearch = wikipedia.page("")             
wikicontent = wikisearch.content             
nlp = en_core_web_sm.load()            
doc = nlp(wikicontent)        

summ_per = summarize(wikicontent, ratio = "")                  
print("Percent summary")            
print(summ_per)           

summ_words = summarize(wikicontent, word_count = "")               
print("Word count summary")                
print(summ_words)         