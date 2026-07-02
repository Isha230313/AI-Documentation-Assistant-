print("[rag.py] NEW VERSION LOADED")
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import ANTHROPIC_MODEL, TEMPERATURE, MAX_TOKENS

load_dotenv()

# Used when docs are retrieved — answer grounded in context
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an AI Documentation Assistant. Answer the user's question using the document excerpts below. "
        "Cite sources inline as [Source: filename].\n\n"
        "Document excerpts:\n{context}"
    )),
    ("human", "{question}"),
])

# Used when no relevant docs found — answer from general knowledge
GENERAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Answer the user's question clearly and concisely. "
               "End your response with: _(General knowledge — not from your uploaded documents.)_"),
    ("human", "{question}"),
])


def format_context(docs) -> str:
    return "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    )


def build_chain():
    return ChatAnthropic(model=ANTHROPIC_MODEL, temperature=TEMPERATURE, max_tokens=MAX_TOKENS)


def ask(question, llm, retriever):
    docs = retriever.invoke(question)

    print(f"\n[DEBUG] Question: {question}")
    print(f"[DEBUG] Docs retrieved: {len(docs)}")

    if docs:
        context = format_context(docs)
        prompt  = RAG_PROMPT
        chain   = prompt | llm | StrOutputParser()
        answer  = chain.invoke({"question": question, "context": context})
        sources = list({doc.metadata.get("source", "unknown") for doc in docs})
    else:
        chain   = GENERAL_PROMPT | llm | StrOutputParser()
        answer  = chain.invoke({"question": question})
        sources = []

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    from embedding import get_embeddings
    from vector import get_retriever

    embeddings = get_embeddings()
    retriever  = get_retriever(embeddings)
    llm        = build_chain()

    print("=" * 50)
    print("  AI Documentation Assistant")
    print("  Type 'quit' to exit.")
    print("=" * 50)

    while True:
        question = input("\nYou: ").strip()
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            print("Goodbye.")
            break
        response = ask(question, llm, retriever)
        print(f"\nAssistant:\n{response['answer']}")
        if response["sources"]:
            print("\nSources:")
            for src in response["sources"]:
                print(f"  - {src}")
