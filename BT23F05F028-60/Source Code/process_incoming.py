import json
import joblib
import numpy as np
import requests

from sklearn.metrics.pairwise import cosine_similarity


# =========================
# Configuration
# =========================
OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "bge-m3"
LLM_MODEL = "llama3.2:latest"
EMBEDDINGS_FILE = "embeddings.joblib"
TOP_RESULTS = 5
REQUEST_TIMEOUT = 120


# =========================
# Embedding
# =========================
def create_embedding(text_list: list[str]) -> list[list[float]]:
    """
    Generate embeddings using Ollama.
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={
                "model": EMBED_MODEL,
                "input": text_list,
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        embeddings = response.json().get("embeddings")

        if not embeddings:
            raise ValueError("No embeddings returned from API.")

        return embeddings

    except requests.RequestException as exc:
        raise RuntimeError(f"Embedding API request failed: {exc}") from exc


# =========================
# Inference
# =========================
def inference(prompt: str) -> str:
    """
    Generate response using Ollama.
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        result = response.json()
        return result.get("response", "No response generated.")

    except requests.RequestException as exc:
        return f"Generation failed: {exc}"


# =========================
# Prompt Builder
# =========================
def build_prompt(retrieved_chunks_json: str, query: str) -> str:
    return f"""
Here are video chunks containing title, number, start timestamp,
end timestamp and text content of the chunk.

Answer the user's question ONLY using the provided chunks.

{retrieved_chunks_json}

---------------------------------------------------------------------

User Question:
"{query}"

Instructions:

1. Answer based only on the provided chunks.
2. Mention:
   - Which video contains the answer.
   - Relevant timestamps.
   - What is taught in those timestamps.
3. Guide the user to the most relevant video section.
4. If the question is unrelated to the provided video content,
   clearly state that you can only answer questions related
   to the provided videos.
""".strip()


# =========================
# Main
# =========================
def main() -> None:

    try:
        df = joblib.load(EMBEDDINGS_FILE)
    except Exception as exc:
        print(f"Failed to load '{EMBEDDINGS_FILE}': {exc}")
        return

    embedding_matrix = np.vstack(df["embedding"])

    while True:

        incoming_query = input("\nAsk a Question (or type 'exit'): ").strip()

        if incoming_query.lower() == "exit":
            print("Goodbye!")
            break

        if not incoming_query:
            print("Please enter a valid question.")
            continue

        try:
            question_embedding = create_embedding([incoming_query])[0]

            similarities = cosine_similarity(
                embedding_matrix,
                [question_embedding]
            ).flatten()

            top_indices = similarities.argsort()[::-1][:TOP_RESULTS]

            retrieved_df = df.iloc[top_indices]

            chunks_json = json.dumps(
                json.loads(
                    retrieved_df[
                        ["title", "number", "start", "end", "text"]
                    ].to_json()
                ),
                indent=2,
            )

            prompt = build_prompt(
                retrieved_chunks_json=chunks_json,
                query=incoming_query,
            )

            print("\nTop Matching Chunks:\n")

            for rank, (_, row) in enumerate(
                retrieved_df.iterrows(),
                start=1,
            ):
                print(f"Rank #{rank}")
                print(f"Similarity : {similarities[row.name]:.4f}")
                print(f"Title      : {row['title']}")
                print(f"Number     : {row['number']}")
                print(f"Start      : {row['start']}")
                print(f"End        : {row['end']}")
                print(f"Text       : {row['text']}")
                print("-" * 100)

            answer = inference(prompt)

            print("\nAssistant Response:\n")
            print(answer)

        except Exception as exc:
            print(f"\nError: {exc}")


if __name__ == "__main__":
    main()