import requests


LLM_URL = "http://localhost:8080/v1/chat/completions"


def generate_answer(context, question):

    prompt = f"""
You are a regulatory compliance assistant.

Answer the user's question ONLY using the regulatory evidence provided below.

If the evidence is insufficient, say:
"Insufficient information in the regulatory knowledge base."

Do not invent regulations.

REGULATORY EVIDENCE:
{context}

USER QUESTION:
{question}
"""

    response = requests.post(
        LLM_URL,
        json={
            "model": "Qwen3-1.7B",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 300
        },
        timeout=300
    )

    response.raise_for_status()

    answer = response.json()["choices"][0]["message"]["content"]

    answer = answer.replace("</think>", "").strip()

    return answer