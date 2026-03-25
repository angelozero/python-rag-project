from langchain_chroma.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate

CHROMA_PATH = "chunks_db"
MODEL = "llama3.2"

PROMPT_TEMPLATE = """
Responsa a pergunta baseada apenas no seguinte contexto:
{context}

---

Responsa a pergunta baseada apenas no seguinte contexto:
{question}
"""

def main():
    # 1. Prepare the vector database with Ollama embeddings
    embeddings = OllamaEmbeddings(model=MODEL)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # 2. Get the query from the user
    query = input("Digite sua pergunta: ")
    if not query:
        print("Nenhuma pergunta fornecida.")
        return

    # 3. Search the database for the most relevant chunks
    results = db.similarity_search_with_relevance_scores(query, k=3)

    if not results or results[0][1] < 0.3:
        print("Não foi possível encontrar resultados relevantes.")
        return

    # 4. Build the context from the retrieved chunks
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # 5. Build the prompt and call the local LLM
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query)

    llm = ChatOllama(model=MODEL)
    response = llm.invoke(prompt)

    # 6. Show the answer and the sources
    print(f"\n✅ Resposta:\n{response.content}")
    # sources = [doc.metadata.get("source", "desconhecido") for doc, _score in results]
    # print(f"\n📄 Fontes: {sources}")


if __name__ == "__main__":
    main()
