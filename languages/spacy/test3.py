#sentence-transformers/paraphrase-multilingual-mpnet-base-v2
#all-mpnet-base-v2

import spacy
from cosine_similarity import compute_cosine_similarity

nlp = spacy.load("en_core_web_md")

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
texts = [
         "The canine barked loudly.  Then he ate a lot of pizza. ",
         "The dog made a noisy bark. Then he went to the park. ",
         "He ate a lot of pizza. ",
         "He devoured a large quantity of pizza pie.",
         "彼はピザをたくさん食べた。",
         "何も分からない。 私はあなたを愛しています。",

]

text_embeddings = model.encode(texts)

text_embeddings_dict = dict(zip(texts, list(text_embeddings)))


for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        print(f"Cosine similarity between '{texts[i]}' and '{texts[j]}':\n {compute_cosine_similarity(text_embeddings_dict[texts[i]], text_embeddings_dict[texts[j]])}")



