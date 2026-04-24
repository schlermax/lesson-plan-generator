from langchain_cohere import ChatCohere


def get_chat_model(model: str = "command-a-03-2025", temperature: float = 0.7) -> ChatCohere:
    """Initialize and return a Cohere chat model.

    Args:
        model: The Cohere model to use for chat.
        temperature: Temperature for response generation (0-1).

    Returns:
        A ChatCohere instance ready to generate responses.
    """
    return ChatCohere(model=model, temperature=temperature)


def generate_response(chat_model: ChatCohere, prompt: str) -> str:
    """Generate a response from the chat model.

    Args:
        chat_model: A ChatCohere instance.
        prompt: The prompt to send to the model.

    Returns:
        The generated response text.
    """
    from langchain_core.messages import HumanMessage

    response = chat_model.invoke([HumanMessage(content=prompt)])
    return response.content


__all__ = ["get_chat_model", "generate_response"]
