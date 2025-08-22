#pip install spacy
#python -m spacy download en_core_web_md
#python -m spacy download ja_core_news_md
#pip install sentence-transformers
#python -m spacy init fill-config base_config.cfg config.cfg
#python -m spacy init fill-config gpu_config.cfg config.cfg

#python -m spacy train config.cfg --output ./output --paths.train ./train.spacy --paths.dev ./dev.spacy

import spacy
from cosine_similarity import compute_cosine_similarity

nlp = spacy.load("en_core_web_md")

dog_embedding = nlp.vocab["dog"].vector
cat_embedding = nlp.vocab["cat"].vector
apple_embedding = nlp.vocab["apple"].vector
tasty_embedding = nlp.vocab["tasty"].vector
delicious_embedding = nlp.vocab["delicious"].vector
truck_embedding = nlp.vocab["truck"].vector

print(compute_cosine_similarity(dog_embedding, cat_embedding))


print(compute_cosine_similarity(delicious_embedding, tasty_embedding))

print(compute_cosine_similarity(truck_embedding, delicious_embedding))

#how do we investigate the meaning of each axis?  


from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
texts = [
         "The canine barked loudly.",
         "The dog made a noisy bark.",
         "He ate a lot of pizza.",
         "He devoured a large quantity of pizza pie.",
]

text_embeddings = model.encode(texts)

print(type(text_embeddings))

print(text_embeddings.shape)



from cosine_similarity import compute_cosine_similarity

text_embeddings_dict = dict(zip(texts, list(text_embeddings)))

dog_text_1 = "The canine barked loudly."
dog_text_2 = "The dog made a noisy bark."
print(compute_cosine_similarity(text_embeddings_dict[dog_text_1],
                          text_embeddings_dict[dog_text_2]))

pizza_text_1 = "He ate a lot of pizza."
pizza_test_2 = "He devoured a large quantity of pizza pie."
print(compute_cosine_similarity(text_embeddings_dict[pizza_text_1],
                          text_embeddings_dict[pizza_test_2]))

print(compute_cosine_similarity(text_embeddings_dict[dog_text_1],
                          text_embeddings_dict[pizza_text_1]))





# Load your Japanese spaCy model (e.g., a model with word vectors)
nlp = spacy.load("ja_core_news_md") # Or a model you've trained/installed


patterns = [{"label": "COMPONENT", "pattern": "ABCD"}, 
            {"label": "COMPONENT", "pattern": "DEFG"},
            {"label": "COMPONENT", "pattern": "HIJK"},
            {"label": "COMPONENT", "pattern": "KLMN"},
]

ruler = nlp.add_pipe("entity_ruler")

ruler.add_patterns(patterns)

nlp.add_pipe("merge_entities")


jpdoc1 = nlp("これは日本語の文書です。ABCDはコンポーネントの一部です。DEFGはHIJの一部です。")
jpdoc2 = nlp("これは日本のテキストです。HIJ")

for (ent) in jpdoc1.ents:
    print(f"Entity: {ent.text}, Label: {ent.label_}")
for (ent) in jpdoc2.ents:
    print(f"Entity: {ent.text}, Label: {ent.label_}")

similarity_score = jpdoc1.similarity(jpdoc2)
print(f"JP Similarity score: {similarity_score}")


nlp = spacy.load("en_core_web_md")

about_text = (
    "Gus Proto is a Python developer currently"
    " working for a London-based Fintech"
    " company. He is interested in learning"
    " Natural Language Processing."
)
about_doc = nlp(about_text)
for token in about_doc:
    print(
        f"""
TOKEN: {str(token)}
=====
TAG: {str(token.tag_):10} POS: {token.pos_}
EXPLANATION: {spacy.explain(token.tag_)}"""
    )

