from app.rag.hybrid_search import hybrid_search
from app.llm import generate_answer
from app.agents.risk_engine import assess_transaction


def check_transaction(transaction):

    # Step 1: Deterministic risk assessment
    risk = assess_transaction(transaction)

    # Step 2: Search regulatory knowledge base
    question = f"""
Assess the following financial transaction using ONLY the
provided regulatory evidence.

Transaction:
{transaction}

Return the assessment using exactly these sections:

APPLICABLE REGULATIONS:
List the relevant regulatory requirements.

POTENTIAL COMPLIANCE CONCERNS:
List the concerns supported by the evidence.

REQUIRED ACTIONS:
List the actions supported by the evidence.

MISSING INFORMATION:
List information required to make a more complete assessment.

Do not invent regulations or requirements.
If the evidence is insufficient, say:
INSUFFICIENT INFORMATION.
"""

    results = hybrid_search(transaction, top_k=3)

    if not results:
        print("Insufficient regulatory information.")
        return

    # Step 3: Prepare evidence for LLM
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

    # Step 4: Generate explanation
    answer = generate_answer(
        context=context,
        question=question
    )

    # Step 5: Display result
    print("\n================================")
    print("REGULATORY COMPLIANCE CHECK")
    print("================================")

    print("\nTRANSACTION:")
    print(transaction)

    print("\nRISK LEVEL:")
    print(risk["risk_level"])

    print("\nRISK FACTORS:")

    for factor in risk["risk_factors"]:
        print(f"- {factor}")

    print("\nLLM ASSESSMENT:")
    print(answer)

    print("\nEVIDENCE:")

    for result in results:

        chunk = result["chunk"]

        print(
            f"- {chunk['source']} | "
            f"Page {chunk['page']} | "
            f"Chunk {chunk['chunk_id']}"
        )


if __name__ == "__main__":

    transaction = """
    A financial institution is processing a $2 million
    cross-border payment to a counterparty located in a
    high-risk jurisdiction. The counterparty's KYC verification
    has not been completed.
    """

    check_transaction(transaction)