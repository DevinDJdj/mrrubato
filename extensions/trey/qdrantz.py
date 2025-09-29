from qdrant_client import QdrantClient, models
from tqdm import tqdm

qdrantz = None
dense_model_name = "sentence-transformers/all-MiniLM-L6-v2"
sparse_model_name = "prithivida/Splade_PP_en_v1"
dense_vector_name = "dense"
sparse_vector_name = "sparse"

def init_qdrant():
    global qdrantz
    qdrantz = QdrantClient(":memory:") # Create in-memory Qdrant instance, for testing, CI/CD
    # OR

def get_collection(topic):
    global qdrantz
    if qdrantz.collection_exists(topic):
        return qdrantz
    return None

def create_collection(topic, dimension=384):
    global qdrantz
    if not qdrantz.collection_exists(topic):
        qdrantz.create_collection(
            collection_name=topic,
            vectors_config={
                dense_vector_name: models.VectorParams(
                    size=qdrantz.get_embedding_size(dense_model_name), 
                    distance=models.Distance.COSINE
                )
            },  # size and distance are model dependent
            sparse_vectors_config={sparse_vector_name: models.SparseVectorParams()},
        )
    return qdrantz

def add_vectors(topic, vectors, ids=None):
    global qdrantz
    if not qdrantz.collection_exists(topic):
        create_collection(topic)
    if ids is None:
        ids = [i for i in range(len(vectors))]
    print("Adding vectors to Qdrant collection...")
    print(len(vectors), len(ids))
    qdrantz.upsert(
        collection_name=topic,
        points=[
            models.PointStruct(
                id=ids[i],
                vector={
                    dense_vector_name: models.Document(text=vectors[i], model=dense_model_name),
        
                    sparse_vector_name: models.Document(text=vectors[i], model=sparse_model_name),
                },
                payload={"text": vectors[i], "id": ids[i]},
            )
            for i in range(len(vectors))
        ],
    )
    return True


class HybridSearcher:
    DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    SPARSE_MODEL = "prithivida/Splade_PP_en_v1"
    def __init__(self, collection_name, qdrantz=qdrantz):
        self.collection_name = collection_name
        self.qdrant_client = qdrantz

    def search(self, text: str):
        search_result = self.qdrant_client.query_points(
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
            limit=5,  # 5 the closest results
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
    

    hybrid_searcher = HybridSearcher(collection_name="demo_collection", qdrantz=qdrantz)
    results = hybrid_searcher.search(text="What can I see from the moon?")
    print("Search Results:")
    for result in results:
        print(result)
