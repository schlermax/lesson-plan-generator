from services.ingestion.vector_store import VectorRecord


def construct_rag_prompt(
    user_query: str,
    relevant_records: list[VectorRecord],
    system_instruction: str | None = None,
) -> str:
    """Construct a RAG prompt from user query and relevant context.

    Args:
        user_query: The user's question or request.
        relevant_records: List of relevant documents retrieved from vector store.
        system_instruction: Optional system instruction for the lesson plan.

    Returns:
        Formatted prompt string ready for the LLM.
    """
    if not system_instruction:
        system_instruction = (
            "You are an expert lesson plan generator. Based on the provided context "
            "about the learner's prior knowledge and learning style, create a clear and "
            "tailored lesson plan for the requested concept."
        )

    context_parts = []
    for i, record in enumerate(relevant_records, start=1):
        source = record.document.metadata.get("source", "Unknown")
        content = record.document.page_content.strip()
        context_parts.append(f"Context {i} (from {source}):\n{content}")

    context_str = "\n\n".join(context_parts)

    prompt = f"""System Instruction:
{system_instruction}

Relevant Context:
{context_str}

User Query:
{user_query}

Generate a comprehensive and tailored lesson plan based on the above context and query."""

    return prompt


__all__ = ["construct_rag_prompt"]

