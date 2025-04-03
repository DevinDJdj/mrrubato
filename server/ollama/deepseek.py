#>pip install llama-index-llms-deepseek
#>pip install ollama
#>ollama run deepseek-r1:1.5b



import ollama

msg = "Hello, how can you assist me?"

response = ollama.chat(model="deepseek-r1", messages=[{'role': 'user', 'content': msg}])
print(response)