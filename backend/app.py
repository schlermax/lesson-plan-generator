import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify, request

from middleware.cors import setup_cors
from services.generation.chat_model import generate_response, get_chat_model
from services.generation.prompt_template import construct_rag_prompt
from services.ingestion.document_loader import load_text_documents
from services.ingestion.embeddings_model import (
    embed_query,
    embed_texts,
    get_cohere_embeddings,
)
from services.ingestion.text_splitter import split_documents
from services.ingestion.vector_store import InMemoryVectorStore

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Initialize Flask app
app = Flask(__name__)

# Setup CORS
setup_cors(app)

# Global state for RAG pipeline
_vector_store: InMemoryVectorStore | None = None
_embeddings_model = None


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

    documents = load_text_documents(str(root), recursive=True)

    chunks = split_documents(
        documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    embeddings_model = get_cohere_embeddings(model=embedding_model)
    chunk_texts = [chunk.page_content for chunk in chunks]
    embeddings = embed_texts(embeddings_model, chunk_texts)

    vector_store = InMemoryVectorStore()
    vector_store.add(chunks, embeddings)

    return vector_store


def generate_lesson_plan(
    user_query: str,
    vector_store: InMemoryVectorStore,
    embeddings_model,
    chat_model_name: str = "command-a-03-2025",
    k: int = 3,
    system_instruction: str | None = None,
) -> str:
    """Generate a lesson plan using the RAG pipeline."""
    query_embedding = embed_query(embeddings_model, user_query)
    relevant_records = retrieve_top_k(vector_store, query_embedding, k=k)
    rag_prompt = construct_rag_prompt(user_query, relevant_records, system_instruction)
    chat_model = get_chat_model(model=chat_model_name)
    lesson_plan = generate_response(chat_model, rag_prompt)
    return lesson_plan


def init_rag_pipeline():
    """Initialize the RAG pipeline on app startup."""
    global _vector_store, _embeddings_model
    print("Initializing RAG pipeline...")
    _vector_store = run_ingestion_pipeline()
    _embeddings_model = get_cohere_embeddings()
    print(f"RAG pipeline initialized with vector store: {_vector_store}")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/planner", methods=["POST"])
def planner():
    """Planner endpoint that generates lesson plans using RAG pipeline.
    
    Request JSON:
        {
            "query": "Teach me about data structures",
            "k": 3,
            "system_instruction": "Optional custom instruction"
        }
    
    Response JSON:
        {
            "success": true,
            "lesson_plan": "Generated lesson plan text",
            "query": "Original user query"
        }
    """
    if not _vector_store or not _embeddings_model:
        return jsonify({"success": False, "error": "RAG pipeline not initialized"}), 500
    
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"success": False, "error": "Missing 'query' field in request"}), 400
    
    user_query = data.get("query")
    k = data.get("k", 3)
    system_instruction = data.get("system_instruction")
    
    try:
        lesson_plan = generate_lesson_plan(
            user_query=user_query,
            vector_store=_vector_store,
            embeddings_model=_embeddings_model,
            k=k,
            system_instruction=system_instruction,
        )
        return jsonify({
            "success": True,
            "query": user_query,
            "lesson_plan": lesson_plan,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


if __name__ == "__main__":
    init_rag_pipeline()
    app.run(debug=True, host="0.0.0.0", port=6573)