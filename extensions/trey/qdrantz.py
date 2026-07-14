from qdrant_client import QdrantClient, models
from tqdm import tqdm

import logging
qdrantz_client = None
dense_model_name = "sentence-transformers/all-MiniLM-L6-v2"
sparse_model_name = "prithivida/Splade_PP_en_v1"
dense_vector_name = "dense"
sparse_vector_name = "sparse"

logger = logging.getLogger(__name__)

def init_qdrant():
    global qdrantz_client
    if (qdrantz_client is None):
        qdrantz_client = QdrantClient(":memory:") # Create in-memory Qdrant instance, for testing, CI/CD
    # OR
    return qdrantz_client

def get_collection(topic):
    global qdrantz_client
    if qdrantz_client.collection_exists(topic):
        return qdrantz_client
    else:
        return create_collection(topic)
    return None

def create_collection(topic, dimension=384):
    global qdrantz_client
    if not qdrantz_client.collection_exists(topic):
        print(dense_model_name, sparse_model_name)
        qdrantz_client.create_collection(
            collection_name=topic,
            vectors_config={
                dense_vector_name: models.VectorParams(
                    size=qdrantz_client.get_embedding_size(dense_model_name), 
                    distance=models.Distance.COSINE
                )
            },  # size and distance are model dependent
            sparse_vectors_config={sparse_vector_name: models.SparseVectorParams()},
        )
    return qdrantz_client

def add_vectors(topic, texts, ids=None, payloads=None):
    global qdrantz_client
    if not qdrantz_client.collection_exists(topic):
        create_collection(topic)
    print("Adding vectors to Qdrant collection...")
    print(len(texts), ' total')
    ids = ids if ids is not None else list(range(len(texts)))
    lengths = [len(t) for t in texts]
    sorted_lengths = sorted(lengths)
    avg_length = sum(lengths) / len(lengths)

    if payloads is None:
        payloads = []


        for i in range(len(texts)):
            #print(f'Text: {texts[i]}')
            if (len(texts[i]) > avg_length and len(texts[i]) < avg_length * 3):
                payloads.append({"id": ids[i], "text": texts[i]})

    print(len(payloads), ' used')
    qdrantz_client.upsert(
        collection_name=topic,
        points=[
            models.PointStruct(
                id=payloads[i]['id'],
                vector={
                    dense_vector_name: models.Document(text=payloads[i]['text'], model=dense_model_name),
        
                    sparse_vector_name: models.Document(text=payloads[i]['text'], model=sparse_model_name),
                },
                payload=payloads[i],
            )
            for i in range(len(payloads))
        ],
    )
    logging.info(f'Added {len(texts)} texts to Qdrant collection {topic}')

    return True


class HybridSearcher:
    DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    SPARSE_MODEL = "prithivida/Splade_PP_en_v1"
    def __init__(self, collection_name, qdrantz_client=qdrantz_client):
        self.collection_name = collection_name
        self.qdrantz_client = qdrantz_client

    def search(self, text: str, top_k: int = 5):
        search_result = self.qdrantz_client.query_points(
            collection_name=self.collection_name,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF  # we are using reciprocal rank fusion here
            ),
            prefetch=[
                models.Prefetch(
                    query=models.Document(text=text, model=self.DENSE_MODEL),
                    using=dense_vector_name,
                ),
                models.Prefetch(
                    query=models.Document(text=text, model=self.SPARSE_MODEL),
                    using=sparse_vector_name,
                ),
            ],
            query_filter=None,  # If you don't want any filters for now
            limit=top_k,  # 5 the closest results
        ).points
        # `search_result` contains models.QueryResponse structure
        # We can access list of scored points with the corresponding similarity scores,
        # vectors (if `with_vectors` was set to `True`), and payload via `points` attribute.

        # Select and return metadata
        metadata = [point.payload for point in search_result]
        return metadata
    
if (__name__ == "__main__"):

#    qdrant = QdrantClient(":memory:") # Create in-memory Qdrant instance, for testing, CI/CD
    # OR
#    client = QdrantClient(path="path/to/db")  # Persists changes to disk, fast prototyping
    init_qdrant()
    create_collection(topic="demo_collection",)
    from fastembed import (
                SparseTextEmbedding,
                TextEmbedding,
                ImageEmbedding,
                LateInteractionMultimodalEmbedding,
                LateInteractionTextEmbedding,
            )


    # Example documents to add to the collection.
    documents = [
        {"id": 1, "description": "The Eiffel Tower is located in Paris."},
        {"id": 2, "description": "The Great Wall of China is visible from space."},
        {"id": 3, "description": "The Pyramids of Giza are ancient wonders."},
        {"id": 4, "description": "The Statue of Liberty is in New York City."},
        {"id": 5, "description": "Machu Picchu is an Incan citadel in Peru."},
    ]
    texts = [doc["description"] for doc in documents]
    ids = [doc["id"] for doc in documents]
    add_vectors(topic="demo_collection", vectors=texts, ids=ids)
    

    hybrid_searcher = HybridSearcher(collection_name="demo_collection", qdrantz_client=qdrantz_client)
    results = hybrid_searcher.search(text="What can I see from the moon?")
    print("Search Results:")
    for result in results:
        print(result)
