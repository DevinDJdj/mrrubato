
ollama create my-ollama3-model -f custom.param
ollama list

"""
[INST]<<SYS>>
All the $$context given has been used up to this point to make a software product.  
Use the given $$context to answer @@Questions. 
Please follow the following rules:
1. Try to find the answers or suggestions in the $$context given.  
2. If you find the answer, write the answer in a concise way and add the list of sources that were used to derive the answer. 
3. If you do not find the answer, please say you couldnt find the answer, but find similar content in the $$context.  
4. Optionally suggest something that the user could do next based on the $$context.  
<</SYS>>
{context}

Question: {question}
Helpful Answer:
[/INST]
"""

"""
The following are ordered notes from a project.  
There are some definitions in **book/definitions.txt
which show some special rules regarding the syntax of how these notes were made.  
Please answer the next questions based on the notes.  

@@Question ...

@@Question Which parts of which documents did you use to attain the answer?  

--NOTE ...



"""