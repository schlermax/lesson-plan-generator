from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document


def load_text_documents(directory_path: str, recursive: bool = True, encoding: str = "utf-8") -> list[Document]:
    """Load .txt files from a directory using LangChain and return Document objects.

    Args:
        directory_path: Directory containing text files.
        recursive: If True, search subdirectories recursively.
        encoding: File encoding used when reading .txt files.

    Returns:
        A list of LangChain Document objects.

    Raises:
        FileNotFoundError: If the path does not exist.
        NotADirectoryError: If the path is not a directory.
    """
    path = Path(directory_path)

    if not path.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")

    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")

    glob_pattern = "**/*.txt" if recursive else "*.txt"
    loader = DirectoryLoader(
        path,
        glob=glob_pattern,
        loader_cls=TextLoader,
        loader_kwargs={"encoding": encoding},
    )

    documents = loader.load()
    for document in documents:
        metadata = dict(document.metadata or {})
        metadata.setdefault("source", metadata.get("source", ""))
        document.metadata = metadata
    return documents


__all__ = ["load_text_documents"]
