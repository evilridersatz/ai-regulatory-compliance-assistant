from app.rag.hybrid_search import hybrid_search
from app.llm import generate_answer


def run_rag(question):

    results = hybrid_search(question, top_k=3)

    if not results:
        print("No relevant regulatory evidence found.")
        return

    context_parts = []

    for result in results:

        chunk = result["chunk"]

        context_parts.append(
            f"""
SOURCE: {chunk['source']}
PAGE: {chunk['page']}
CHUNK: {chunk['chunk_id']}

{chunk['text']}
"""
        )

    context = "\n".join(context_parts)

    answer = generate_answer(
        context=context,
        question=question
    )

    print("\n================================")
    print("RAG COMPLIANCE ANSWER")
    print("================================")

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)

    print("\nSources:")

    for result in results:

        chunk = result["chunk"]

        print(
            f"- {chunk['source']} | "
            f"Page {chunk['page']} | "
            f"Chunk {chunk['chunk_id']}"
        )


if __name__ == "__main__":

    question = (
        "What should happen when a transaction involves "
        "a customer from a high-risk jurisdiction?"
    )

    run_rag(question)