from pathlib import Path
from pypdf import PdfReader
import re

DATA_DIR = Path("data/regulations")


def load_pdf(file_path: Path):
    reader = PdfReader(str(file_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "text": text,
            "page": page_number,
            "source": file_path.name
        })

    return pages


def create_chunks(pages):
    chunks = []
    chunk_id = 0

    for page in pages:
        paragraphs = re.split(r"\n\s*\n", page["text"])

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if len(paragraph) < 50:
                continue

            chunks.append({
                "chunk_id": chunk_id,
                "text": paragraph,
                "source": page["source"],
                "page": page["page"]
            })

            chunk_id += 1

    return chunks


def load_all_documents():
    all_chunks = []

    pdf_files = list(DATA_DIR.glob("*.pdf"))

    for pdf_file in pdf_files:

        print(f"\nProcessing: {pdf_file.name}")

        try:
            pages = load_pdf(pdf_file)
            chunks = create_chunks(pages)

            all_chunks.extend(chunks)

            print(f"  Pages: {len(pages)}")
            print(f"  Chunks: {len(chunks)}")

        except Exception as e:
            print(f"  ERROR: {e}")
            print("  Skipping this document.")

    return all_chunks


if __name__ == "__main__":

    chunks = load_all_documents()

    print("\n==============================")
    print("INGESTION SUMMARY")
    print("==============================")

    print("Total chunks:", len(chunks))

    for chunk in chunks[:10]:
        print("\n--- CHUNK ---")
        print("Source:", chunk["source"])
        print("Page:", chunk["page"])
        print("ID:", chunk["chunk_id"])
        print("Text:", chunk["text"][:300])