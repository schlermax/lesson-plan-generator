from typing import Iterable

from langchain_core.documents import Document


def split_document_text(
    document: Document,
    chunk_size: int = 100,
    chunk_overlap: int = 40,
) -> list[Document]:
    """Split a single LangChain Document into overlapping character chunks."""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = document.page_content or ""
    chunks: list[Document] = []
    start = 0
    chunk_index = 1

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        metadata = dict(document.metadata or {})
        metadata["source"] = metadata.get("source", "")
        metadata["chunk_index"] = chunk_index
        metadata["chunk_start"] = start
        metadata["chunk_end"] = end

        chunks.append(Document(page_content=chunk_text, metadata=metadata))
        chunk_index += 1

        if end == len(text):
            break
        start += chunk_size - chunk_overlap

    return chunks


def split_documents(
    documents: Iterable[Document],
    chunk_size: int = 100,
    chunk_overlap: int = 40,
) -> list[Document]:
    """Split a collection of LangChain Documents into character chunks."""
    all_chunks: list[Document] = []
    for document in documents:
        all_chunks.extend(split_document_text(document, chunk_size=chunk_size, chunk_overlap=chunk_overlap))
    return all_chunks
