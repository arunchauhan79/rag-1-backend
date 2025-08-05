import os
from pathlib import Path
from typing import List, Dict, Any
from utils import get_vectorstore
from core import logger, BadRequestException
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from schema import ProcessPDFResponse

def _get_pdf_folder() -> Path:
    """Get the PDF folder path."""
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "uploaded_files"


def _load_pdf_documents(pdf_folder: Path) -> List[Document]:
    """Load all PDF documents from the specified folder."""
    loader = DirectoryLoader(
        path=str(pdf_folder),
        glob='*.pdf',
        loader_cls=PyPDFLoader
    )
    return loader.load()


def _cleanup_processed_files(pdf_folder: Path) -> None:
    """Remove all files from the PDF folder after processing."""
    for filename in os.listdir(pdf_folder):
        file_path = pdf_folder / filename
        if file_path.is_file():
            file_path.unlink()


def _create_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create and configure the text splitter."""
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "],
        length_function=len
    )


def _add_organization_metadata(chunks: List[Document], org_id: str) -> List[Document]:
    """Add organization ID to chunk metadata."""
    for chunk in chunks:
        chunk.metadata = {'orgId' : org_id}
    return chunks


def _store_chunks_in_vectorstore(chunks: List[Document]) -> None:
    """Store document chunks in the vector database."""
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)


def process_all_pdfs(org_id: str) -> Dict[str, Any]:
    """
    Process all PDF files for the given organization.
    
    Args:
        org_id: Organization identifier
        
    Returns:
        Dict containing processing results
        
    Raises:
        BadRequestException: If processing fails
    """
    try:
        logger.info(f"Starting PDF processing for organization: {org_id}")
        
        # Step 1: Get PDF folder and load documents
        pdf_folder = _get_pdf_folder()
        docs = _load_pdf_documents(pdf_folder)
        
        if not docs:
            logger.info("No PDF documents found to process")
            return {"status": "success", "message": "No documents to process", "chunks_processed": 0}
        
        logger.info(f"Loaded {len(docs)} document pages")
        
        # Step 2: Clean up processed files
        _cleanup_processed_files(pdf_folder)
        
        # Step 3: Split documents into chunks
        text_splitter = _create_text_splitter()
        all_chunks = text_splitter.split_documents(docs)
        
        logger.info(f"Created {len(all_chunks)} chunks from documents")
        
        # Step 4: Add organization metadata
        chunks_with_metadata = _add_organization_metadata(all_chunks, org_id)
        
        # Step 5: Store in vector database
        _store_chunks_in_vectorstore(chunks_with_metadata)
        
        logger.info(f"Successfully processed {len(chunks_with_metadata)} chunks for organization {org_id}")
        
        return ProcessPDFResponse(
            status = "success",
            message= f"Processed {len(chunks_with_metadata)} chunks",
            chunks_processed= len(chunks_with_metadata),
            documents_loaded = len(docs)
        )
        
    except Exception as e:
        logger.error(f"Error processing PDFs for organization {org_id}: {str(e)}")
        raise BadRequestException(f"Error in processing PDF: {str(e)}")       



