#https://www.geeksforgeeks.org/doc2vec-in-nlp/
#pip install gensim
#pip install nltk
#pip install spacy
#python -m spacy download en_core_web_sm

"""
def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)


article = nlp(text)
labels = [x.label_ for x in article.ents]
Counter(labels)

"""
import gensim.models as g
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import nltk
from nltk.tokenize import word_tokenize
import os
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")


nltk.download('punkt')
# define a list of documents.
data = ["This is the first document",
        "This is the second document",
        "This is the third document",
        "This is the fourth document"]
 
# preproces the documents, and create TaggedDocuments
tagged_data = [TaggedDocument(words=word_tokenize(doc.lower()),
                              tags=[str(i)]) for i,
               doc in enumerate(data)]
 
# train the Doc2vec model
#actually based on others seems we shouldnt load a model, 
#but retrain from scratch from time to time.  
if (os.path.exists('doc2vec.model')):
    model = g.Doc2Vec.load('doc2vec.model')
    print('model loaded')
else:
    print('initiating model')
    model = Doc2Vec(vector_size=20,
                min_count=2, epochs=50)
    model.build_vocab(tagged_data)
    model.train(tagged_data,
            total_examples=model.corpus_count,
            epochs=model.epochs)
 
# get the document vectors
document_vectors = [model.infer_vector(
    word_tokenize(doc.lower())) for doc in data]
 
#  print the document vectors
for i, doc in enumerate(data):
    print("Document", i+1, ":", doc)
    print("Vector:", document_vectors[i])
    print()

model.save('doc2vec.model')


def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent


#usage
#why do we have to split this?  Anyway...
testdoc = "this is a sentence number 5."
article = nlp(testdoc)
labels = [(x.text, x.label_) for x in article.ents]
print(Counter(labels))
print(labels)

details = [(x, x.ent_iob_, x.ent_type_) for x in article]
print(details)



tokens = testdoc.split()
new_vector = model.infer_vector(tokens)
sims = model.dv.most_similar([new_vector])
print(sims)
