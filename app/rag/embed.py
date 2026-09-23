from sentence_transformers import SentenceTransformer
from app.rag.chunk import load_pdf, create_chunks
from pathlib import Path

DATA_DIR = Path("data/regulations")

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings():
    pdf_files = list(DATA_DIR.glob("*.pdf"))

    all_chunks = []

    for pdf_file in pdf_files:
        pages = load_pdf(pdf_file)
        chunks = create_chunks(pages)

        all_chunks.extend(chunks)

    texts = [chunk["text"] for chunk in all_chunks]

    embeddings = model.encode(texts)

    print("Chunks:", len(all_chunks))
    print("Embedding shape:", embeddings.shape)

    return all_chunks, embeddings


if __name__ == "__main__":
    create_embeddings()