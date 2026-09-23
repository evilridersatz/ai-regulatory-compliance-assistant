from pathlib import Path

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi

from app.rag.chunk import load_pdf, create_chunks


DATA_DIR = Path("data/regulations")
COLLECTION_NAME = "regulations"

client = QdrantClient(path="data/qdrant")

model = SentenceTransformer("all-MiniLM-L6-v2")

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def load_all_chunks():

    all_chunks = []

    for pdf_file in DATA_DIR.glob("*.pdf"):

        try:
            pages = load_pdf(pdf_file)
            chunks = create_chunks(pages)
            all_chunks.extend(chunks)

        except Exception as e:

            print(f"Skipping {pdf_file.name}: {e}")

    return all_chunks


def hybrid_search(query, top_k=3):

    chunks = load_all_chunks()

    # -------------------------
    # 1. BM25 keyword search
    # -------------------------

    tokenized_chunks = [
        chunk["text"].lower().split()
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_chunks)

    query_tokens = query.lower().split()

    bm25_scores = bm25.get_scores(query_tokens)

    bm25_results = sorted(
        zip(chunks, bm25_scores),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    # -------------------------
    # 2. Vector search
    # -------------------------

    query_embedding = model.encode(query)

    vector_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=10
    )

    # -------------------------
    # 3. Combine results
    # -------------------------

    results = {}

    for chunk, score in bm25_results:

        key = (
            chunk["source"],
            chunk["page"],
            chunk["chunk_id"]
        )

        results[key] = {
            "chunk": chunk,
            "bm25_score": float(score),
            "vector_score": 0.0
        }

    for result in vector_results.points:

        payload = result.payload

        key = (
            payload["source"],
            payload["page"],
            payload["chunk_id"]
        )

        if key not in results:

            results[key] = {
                "chunk": payload,
                "bm25_score": 0.0,
                "vector_score": 0.0
            }

        results[key]["vector_score"] = float(result.score)

    # -------------------------
    # 4. Hybrid score
    # -------------------------

    for item in results.values():

        item["combined_score"] = (
            0.5 * item["vector_score"]
            + 0.5 * item["bm25_score"]
        )

    # -------------------------
    # 5. Cross-encoder reranking
    # -------------------------

    candidate_results = sorted(
        results.values(),
        key=lambda x: x["combined_score"],
        reverse=True
    )[:10]

    pairs = [
        (query, item["chunk"]["text"])
        for item in candidate_results
    ]

    rerank_scores = reranker.predict(pairs)

    for item, score in zip(
        candidate_results,
        rerank_scores
    ):

        item["rerank_score"] = float(score)

    # -------------------------
    # 6. Final ranking
    # -------------------------

    ranked_results = sorted(
        candidate_results,
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return ranked_results[:top_k]


# -------------------------
# Test
# -------------------------

if __name__ == "__main__":

    query = "high-risk customers enhanced due diligence"

    results = hybrid_search(query)

    print("\nQUERY:")
    print(query)

    for i, result in enumerate(results, start=1):

        chunk = result["chunk"]

        print("\n==============================")
        print(f"RESULT {i}")
        print("==============================")

        print(
            "Combined Score:",
            result["combined_score"]
        )

        print(
            "Vector Score:",
            result["vector_score"]
        )

        print(
            "BM25 Score:",
            result["bm25_score"]
        )

        print(
            "Rerank Score:",
            result["rerank_score"]
        )

        print(
            "Source:",
            chunk["source"]
        )

        print(
            "Page:",
            chunk["page"]
        )

        print("Text:")
        print(chunk["text"][:1000])