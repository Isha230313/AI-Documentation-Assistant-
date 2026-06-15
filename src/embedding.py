from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from config import EMBEDDING_MODEL

load_dotenv()


def get_embeddings():
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)
