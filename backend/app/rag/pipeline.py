from backend.app.agents.client import client
from backend.app.rag.vector_store import index_knowledge, retrieve


RAG_MODEL = "qwen/qwen3.8-27b"


def ask_rag(question: str) -> dict:
    retrieved = retrieve(question, n_results=3)

    context = "\n\n".join(
        f"[Source: {item['source']} | Chunk: {item['chunk']}]\n"
        f"{item['document']}"
        for item in retrieved
    )

    completion = client.chat.completions.create(
        model=RAG_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a retrieval-augmented generation assistant. "
                    "Answer the user's question using only the retrieved context. "
                    "Do not use outside knowledge. "
                    "If the context does not contain the answer, explicitly say "
                    "that the knowledge base does not contain enough information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Retrieved context:\n\n{context}\n\n"
                    f"Question: {question}"
                ),
            },
        ],
    )

    return {
        "question": question,
        "answer": completion.choices[0].message.content,
        "retrieved_context": retrieved,
        "vector_database": "ChromaDB",
        "model": RAG_MODEL,
    }


if __name__ == "__main__":
    count = index_knowledge()

    print(f"Indexed chunks: {count}")
    print("Vector database: ChromaDB")
    print()

    result = ask_rag("How does the Task Agent access task data?")

    print("Question:")
    print(result["question"])

    print("\nRetrieved context:")
    for item in result["retrieved_context"]:
        print(
            f"- chunk={item['chunk']} "
            f"distance={item['distance']}: "
            f"{item['document']}"
        )

    print("\nRAG Answer:")
    print(result["answer"])
