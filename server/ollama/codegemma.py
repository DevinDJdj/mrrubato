import ollama

response = ollama.chat(model="codegemma", messages=[{'role': 'user', 'content': "Hello, how can you assist me?"}])
print(response)