#languages/helpers/spacy/test.py
import time


#transformers NER
from transformers import pipeline
    
lag = time.time()
ner_pipeline = pipeline("ner", aggregation_strategy="simple")
results = ner_pipeline("Bill Gates founded Microsoft in Redmond.")
print(results)
print("Time taken:", time.time() - lag)


from transformers import AutoTokenizer, AutoModelForTokenClassification
lag = time.time()
tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

nlp = pipeline("ner", model=model, tokenizer=tokenizer)
example = "My name is Wolfgang and I live in Berlin"

ner_results = nlp(example)
print(ner_results)
print("Time taken:", time.time() - lag)


#NLTK NER
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
lag = time.time()    
# Download necessary resources
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('maxent_ne_chunker_tab')
nltk.download('words')

# Sample sentence
sentence = "Apple is looking at buying U.K. startup for $1 billion."

# Tokenize and POS tag
tokens = word_tokenize(sentence)
pos_tags = pos_tag(tokens)

# Perform NER
named_entities = ne_chunk(pos_tags)
print(named_entities)
print("Time taken:", time.time() - lag)


#transformers with real test data..
lag = time.time()
tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

with open("./book/20260816.txt", "r", encoding="utf-8") as f:
    text = f.read()

example = text

ner_results = nlp(example)
print(ner_results)
print("Time taken:", time.time() - lag)


lag = time.time()
ner_pipeline = pipeline("ner", aggregation_strategy="simple")
results = ner_pipeline(example)
print(results)
print("Time taken:", time.time() - lag)
