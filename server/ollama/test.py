#ollama serve
#ollama run llama2
#python ./test.py
#why is ./load.py not working?? changed to fastembed
import requests
import json

url = 'http://localhost:8181/api/generate'

myobj = {'model': 'llama2', 'stream': False, 'prompt': 'Why is the sky Blue?'}
myobj = {'model': 'llama2', 'stream': False, 'prompt': 'Who wrote the document Orca: Progressive Learning from Complex Explanation Traces of GPT-4'}
print(myobj['prompt'])
x = requests.post(url, json = myobj)

print(x.text)
obj = json.loads(x.text)
print(obj['response'])

