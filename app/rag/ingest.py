from pathlib import Path
from pypdf import PdfReader


DATA_DIR = Path("data/regulations")


def load_pdf(file_path: Path) -> str:
    """Extract text from a PDF."""
    reader = PdfReader(str(file_path))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages)


def load_all_pdfs():
    """Load all regulatory PDFs from the data directory."""

    documents = []

    for pdf_file in DATA_DIR.glob("*.pdf"):
        text = load_pdf(pdf_file)

        documents.append(
            {
                "source": pdf_file.name,
                "text": text,
            }
        )

    return documents


if __name__ == "__main__":
    documents = load_all_pdfs()

    print(f"Documents found: {len(documents)}")

    for document in documents:
        print(
            f"{document['source']} -> "
            f"{len(document['text'])} characters"
        )