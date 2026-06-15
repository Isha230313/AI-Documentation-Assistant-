from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from config import ANTHROPIC_MODEL, TEMPERATURE, MAX_TOKENS

load_dotenv()

PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an AI Documentation Assistant. "
        "Answer using ONLY the context below. "
        "Cite the source for every claim. "
        "If the answer is not in the context, say so.\n\n"
        "Context:\n{context}"
    )),
    ("human", "{question}"),
])


def format_context(docs) -> str:
    return "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    )


def build_chain(retriever):
    llm = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=TEMPERATURE, max_tokens=MAX_TOKENS)

    return (
        RunnableParallel({
            "context":  retriever | format_context,
            "question": RunnablePassthrough(),
        })
        | PROMPT
        | llm
        | StrOutputParser()
    )


def ask(question, chain, retriever):
    docs    = retriever.invoke(question)
    answer  = chain.invoke(question)
    sources = list({doc.metadata.get("source", "unknown") for doc in docs})
    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    from embedding import get_embeddings
    from vector import get_retriever

    embeddings = get_embeddings()
    retriever  = get_retriever(embeddings)
    chain      = build_chain(retriever)

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

        response = ask(question, chain, retriever)
        print(f"\nAssistant:\n{response['answer']}")
        print("\nSources:")
        for src in response["sources"]:
            print(f"  - {src}")
