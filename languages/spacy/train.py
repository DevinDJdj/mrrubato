#pip install spacy[transformers]
#https://www.newscatcherapi.com/blog/train-custom-named-entity-recognition-ner-model-with-spacy-v3

#python -m spacy init fill-config test.cfg config.cfg
import json
 
with open('Corona2.json', 'r') as f:
    data = json.load(f)
    
print(data['examples'][0])


training_data = {'classes' : ['MEDICINE', "MEDICALCONDITION", "PATHOGEN"], 'annotations' : []}
for example in data['examples']:
  temp_dict = {}
  temp_dict['text'] = example['content']
  temp_dict['entities'] = []
  for annotation in example['annotations']:
    start = annotation['start']
    end = annotation['end']
    label = annotation['tag_name'].upper()
    temp_dict['entities'].append((start, end, label))
  training_data['annotations'].append(temp_dict)
  
print(training_data['annotations'][0])

import spacy
from spacy.tokens import DocBin
from tqdm import tqdm

nlp = spacy.blank("en") # load a new spacy model
doc_bin = DocBin() # create a DocBin object



from spacy.util import filter_spans

for training_example  in tqdm(training_data['annotations']): 
    text = training_example['text']
    labels = training_example['entities']
    doc = nlp.make_doc(text) 
    ents = []
    for start, end, label in labels:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    filtered_ents = filter_spans(ents)
    doc.ents = filtered_ents 
    doc_bin.add(doc)

doc_bin.to_disk("training_data.spacy") # save the docbin object


#from spacy.cli.train import train

#train("./config.cfg", overrides={"paths.train": "./training_data.spacy", "paths.dev": "./training_data.spacy"})

#pip install cupy
#python -m spacy train config.cfg --output ./ --paths.train ./training_data.spacy --paths.dev ./training_data.spacy

#python ./test2.py