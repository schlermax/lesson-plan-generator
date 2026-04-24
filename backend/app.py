from pathlib import Path

from services.ingestion.document_loader import load_text_documents


def run_loader_test(directory_path: str | Path | None = None) -> list:
    root = Path(directory_path or Path(__file__).resolve().parent / "mock_data")
    print(f"Loading documents from: {root}")

    documents = load_text_documents(str(root), recursive=True)
    print(f"Loaded {len(documents)} documents")

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "<no source>")
        snippet = document.page_content.strip().replace("\n", " ")[:120]
        print(f"{index}. source={source}, length={len(document.page_content)}")
        print(f"   {snippet}{'...' if len(document.page_content) > 120 else ''}")

    return documents


if __name__ == "__main__":
    run_loader_test()
