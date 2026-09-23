from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.rag.embed import create_embeddings

COLLECTION_NAME = "regulations"

client = QdrantClient(path="data/qdrant")


def create_vector_store():

    chunks, embeddings = create_embeddings()

    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    points = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        points.append(
            PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"]
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print("Vector store created successfully.")
    print("Vectors stored:", len(points))


if __name__ == "__main__":
    create_vector_store()