from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "regulations"

client = QdrantClient(path="data/qdrant")

model = SentenceTransformer("all-MiniLM-L6-v2")

query = "What are the requirements for customers from high-risk jurisdictions?"

query_embedding = model.encode(query)

results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_embedding.tolist(),
    limit=3
)

for result in results.points:

    print("\n--- RESULT ---")
    print("Score:", result.score)
    print("Source:", result.payload["source"])
    print("Page:", result.payload["page"])
    print("Text:")
    print(result.payload["text"])