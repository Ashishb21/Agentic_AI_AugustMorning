

text_chunks = [
    "The Great Fire of London in 1666 destroyed over 13,000 houses.",
    "Julius Caesar was assassinated on the Ides of March (March 15) in 44 BCE.",
    "The Black Death, is estimated to have killed nearly one-third of the \
        population",
]

users_question = "Tell me something interesting about diseases in history" 

from langchain_ollama import OllamaEmbeddings
import numpy as np

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "qwen3-embedding:latest"

# Create the client once and reuse it for every call
embeddings = OllamaEmbeddings(
    model=MODEL_NAME,
    base_url=OLLAMA_URL,
)

def get_embedding(text: str) -> np.ndarray:
    return np.array(embeddings.embed_query(text))

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2)
    )


chunk_embeddings = [
    get_embedding(chunk) for chunk in text_chunks
]

# Create embedding for user query
query_embedding = get_embedding(users_question)

similarities = []

for idx, emb in enumerate(chunk_embeddings):
    score = cosine_similarity(query_embedding, emb)
    similarities.append((text_chunks[idx], score))

# Sort by highest similarity
similarities.sort(key=lambda x: x[1], reverse=True)

print("Most relevant results:\n")

for text, score in similarities:
    print(f"Score: {score:.4f}")
    print(f"Text : {text}")
    print("-" * 60)