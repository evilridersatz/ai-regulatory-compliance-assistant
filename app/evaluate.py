import json
from app.rag.hybrid_search import hybrid_search
from app.llm import generate_answer


def load_evaluation_data():
    with open("data/evaluation.json", "r") as f:
        return json.load(f)


def evaluate():

    questions = load_evaluation_data()

    results = []

    for i, item in enumerate(questions, start=1):

        question = item["question"]
        ground_truth = item["ground_truth"]

        print(f"\n[{i}/{len(questions)}] {question}")

        retrieved = hybrid_search(question, top_k=3)

        context_parts = []

        for result in retrieved:

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

        results.append({
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "sources": [
                {
                    "source": r["chunk"]["source"],
                    "page": r["chunk"]["page"],
                    "chunk": r["chunk"]["chunk_id"]
                }
                for r in retrieved
            ]
        })

        print("Answer:", answer)

    with open("data/evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n==============================")
    print("EVALUATION COMPLETE")
    print("==============================")
    print("Questions evaluated:", len(results))
    print("Results saved to: data/evaluation_results.json")


if __name__ == "__main__":
    evaluate()