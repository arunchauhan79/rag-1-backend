from langchain_openai  import OpenAIEmbeddings
from core import settings

embedding_model = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

def get_embedding_model():
    return embedding_model