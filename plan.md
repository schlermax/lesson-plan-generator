Ask for lesson plan for some concept and receive a lesson plan from the llm.

# Ingestion Pipline
- Input knowledge: rich context on prior knowledge about pre-requisite topics
- Document loader to give/package context for langchain to understand
- From the context, separate it into chunks so that the knowledge is more digestable
- Embed into vectors so that we can apply mathematical computations to the "text"
- Configure in-memory vector store. (storing/retrieving vectors)

# Generation Pipeline
- User asks for lesson plan regarding a concept they want to know more about
- Embed the query from the user into a vector to compare to the records in vector store
- Take the top k relevant vectors to the query using the cosine similarity search algorithm
- Use the relevant vectors to construct the prompt. Vectors have metadata that maps back to plaintext of the origin users query and instructions.
- Send to llm and return the result

# API 
- Using Flask for api endpoint "Planner"
- Using Flask over FastAPI as deployment platform only works with wsgi whereas FastAPI is asgi

# Frontend
- Use Next.js to build a simple frontend for the backend API

# Why?
- Efficiently sets up a plan for the user. The llm will provide a more taliored lesson plan to the user based on their prior knowledge.
- The goal of this is to save time for the user so that they don't need to keep supplying the llm with more context.