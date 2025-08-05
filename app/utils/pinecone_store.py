from pinecone import Pinecone, ServerlessSpec

from langchain_pinecone import PineconeVectorStore
from core import settings, BadRequestException
from utils import get_embedding_model

# pinecone.init(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

def create_index():
    try:
        if not pc.has_index(settings.PINECONE_INDEX_NAME):
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")        
        )
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        return index;
    except Exception as e:
        raise BadRequestException(f"Error in creating Pinecone Index {e}")
    
    



def get_vectorstore():
    try:
        embedding_model = get_embedding_model()
        
        index = create_index()
        return PineconeVectorStore(index=index, embedding=embedding_model)
    except Exception as e:
        raise BadRequestException(f"Error in get vector store {e}")