import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

from services.generation.chat_model import generate_response, get_chat_model
from services.generation.prompt_template import construct_rag_prompt
from services.ingestion.document_loader import load_text_documents
from services.ingestion.embeddings_model import embed_query, embed_texts, get_cohere_embeddings
from services.ingestion.text_splitter import split_documents
from services.ingestion.vector_store import InMemoryVectorStore

# Load environment variables from .env file
load_dotenv()


def cosine_similarity(embedding1: list[float], embedding2: list[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    arr1 = np.array(embedding1)
    arr2 = np.array(embedding2)
    dot_product = np.dot(arr1, arr2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


def retrieve_top_k(
    vector_store: InMemoryVectorStore,
    query_embedding: list[float],
    k: int = 3,
):
    """Retrieve top k most similar records from vector store using cosine similarity."""
    records = vector_store.get_all()
    similarities = [
        (record, cosine_similarity(query_embedding, record.embedding))
        for record in records
    ]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [record for record, _ in similarities[:k]]




def run_ingestion_pipeline(
    directory_path: str | Path | None = None,
    chunk_size: int = 100,
    chunk_overlap: int = 40,
    embedding_model: str = "embed-english-v3.0",
) -> InMemoryVectorStore:
    """Run the complete ingestion pipeline: load, chunk, embed, store."""
    root = Path(directory_path or Path(__file__).resolve().parent / "mock_data")
    print(f"Loading documents from: {root}")

    documents = load_text_documents(str(root), recursive=True)
    print(f"Loaded {len(documents)} documents\n")

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "<no source>")
        snippet = document.page_content.strip().replace("\n", " ")[:120]
        print(f"{index}. source={source}, length={len(document.page_content)}")
        print(f"   {snippet}{'...' if len(document.page_content) > 120 else ''}")

    chunks = split_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(f"\nSplit into {len(chunks)} chunks\n")
    for index, chunk in enumerate(chunks, start=1):
        source = chunk.metadata.get("source", "<no source>")
        chunk_index = chunk.metadata.get("chunk_index", index)
        snippet = chunk.page_content.strip().replace("\n", " ")[:120]
        print(f"{index}. source={source}, chunk={chunk_index}, length={len(chunk.page_content)}")
        print(f"   {snippet}{'...' if len(chunk.page_content) > 120 else ''}")

    print(f"\nEmbedding chunks using Cohere model: {embedding_model}")
    embeddings_model = get_cohere_embeddings(model=embedding_model)
    chunk_texts = [chunk.page_content for chunk in chunks]
    embeddings = embed_texts(embeddings_model, chunk_texts)
    print(f"Embedded {len(embeddings)} chunks\n")

    vector_store = InMemoryVectorStore()
    vector_store.add(chunks, embeddings)

    print(f"Vector Store: {vector_store}")
    print(f"Sample records:\n")
    for index, record in enumerate(vector_store.get_all()[:3], start=1):
        source = record.document.metadata.get("source", "<no source>")
        embedding_sample = record.embedding[:5]
        snippet = record.document.page_content.strip().replace("\n", " ")[:100]
        print(f"{index}. source={source}")
        print(f"   text: {snippet}...")
        print(f"   embedding (first 5 dims): {embedding_sample}")
        print()

    return vector_store




def generate_lesson_plan(
    user_query: str,
    vector_store: InMemoryVectorStore,
    embeddings_model,
    chat_model_name: str = "command-a-03-2025",
    k: int = 3,
    system_instruction: str | None = None,
) -> str:
    """Generate a lesson plan using the RAG pipeline.
    
    Args:
        user_query: The user's question about a concept.
        vector_store: The populated vector store with context chunks.
        embeddings_model: The Cohere embeddings model.
        chat_model_name: Name of the Cohere chat model to use.
        k: Number of relevant chunks to retrieve.
        system_instruction: Optional custom system instruction.
    
    Returns:
        Generated lesson plan as a string.
    """
    print(f"\n{'='*60}")
    print(f"GENERATION PIPELINE")
    print(f"{'='*60}")
    print(f"User Query: {user_query}\n")

    # Step 1: Embed the user query
    print("[1/4] Embedding user query...")
    query_embedding = embed_query(embeddings_model, user_query)
    print(f"Query embedding dimension: {len(query_embedding)}\n")

    # Step 2: Retrieve top k relevant chunks
    print(f"[2/4] Retrieving top {k} relevant chunks...")
    relevant_records = retrieve_top_k(vector_store, query_embedding, k=k)
    print(f"Retrieved {len(relevant_records)} relevant records:")
    for i, record in enumerate(relevant_records, start=1):
        source = record.document.metadata.get("source", "Unknown")
        snippet = record.document.page_content.strip().replace("\n", " ")[:80]
        print(f"  {i}. {source} - {snippet}...")
    print()

    # Step 3: Construct RAG prompt
    print("[3/4] Constructing RAG prompt...")
    rag_prompt = construct_rag_prompt(user_query, relevant_records, system_instruction)
    print(f"Prompt length: {len(rag_prompt)} characters\n")

    # Step 4: Generate response using chat model
    print(f"[4/4] Generating lesson plan with {chat_model_name}...")
    chat_model = get_chat_model(model=chat_model_name)
    lesson_plan = generate_response(chat_model, rag_prompt)
    print("\nGenerated Lesson Plan:")
    print("-" * 60)
    print(lesson_plan)
    print("-" * 60)

    return lesson_plan


if __name__ == "__main__":
    # Run ingestion pipeline to build vector store
    vector_store = run_ingestion_pipeline()

    # Example generation pipeline
    embeddings_model = get_cohere_embeddings()
    example_query = "Teach me about data structures and their applications"
    lesson_plan = generate_lesson_plan(
        user_query=example_query,
        vector_store=vector_store,
        embeddings_model=embeddings_model,
        k=3,
    )
