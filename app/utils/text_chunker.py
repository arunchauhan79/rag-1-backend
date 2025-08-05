from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

from core import settings

def num_tokens(text):
    encoding = tiktoken.encoding_for_model(settings.EMBEDDING_MODEL)
    return len(encoding.encode(text))


def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=num_tokens
        )
    

def chunk_text(text):
    splitter = get_text_splitter()
    return splitter.split_text(text)

