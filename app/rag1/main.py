import os
from pathlib import Path
from typing import List, Dict, Any, Optional
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


def _load_pdf_documents_with_metadata(pdf_folder: Path, document_mappings: Dict[str, str]) -> List[Document]:
    """Load all PDF documents from the specified folder and add only document IDs to metadata."""
    loader = DirectoryLoader(
        path=str(pdf_folder),
        glob='*.pdf',
        loader_cls=PyPDFLoader
    )
    docs = loader.load()
    
    # Clean metadata and add only document IDs based on filename mapping
    for doc in docs:
        # Extract the unique filename from the document source
        source_path = doc.metadata.get('source', '') if doc.metadata else ''
        filename = os.path.basename(source_path)
        
        # Clear all existing metadata
        doc.metadata = {}
        
        # Find the corresponding document ID and add only that
        document_id = document_mappings.get(filename)
        if document_id:
            doc.metadata['documentId'] = document_id
            logger.info(f"Added document ID {document_id} to {filename}")
        else:
            logger.warning(f"No document ID found for {filename}")
    
    return docs


def _load_pdf_documents(pdf_folder: Path) -> List[Document]:
    """Load all PDF documents from the specified folder and clean metadata."""
    loader = DirectoryLoader(
        path=str(pdf_folder),
        glob='*.pdf',
        loader_cls=PyPDFLoader
    )
    docs = loader.load()
    
    # Clean all metadata from documents
    for doc in docs:
        doc.metadata = {}
    
    return docs


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
    """Clean all metadata and add only orgId and documentId."""
    for chunk in chunks:
        # Store documentId if it exists before cleaning
        document_id = None
        if hasattr(chunk, 'metadata') and chunk.metadata:
            document_id = chunk.metadata.get('documentId')
        
        # Clear all metadata and set only required fields
        chunk.metadata = {'orgId': org_id}
        
        # Add documentId if it was present
        if document_id:
            chunk.metadata['documentId'] = document_id
        
        # Log the cleaned metadata
        logger.debug(f"Cleaned chunk metadata: {chunk.metadata}")
    
    return chunks


def _store_chunks_in_vectorstore(chunks: List[Document]) -> None:
    """Store document chunks in the vector database."""
    vectorstore = get_vectorstore()
    
    # Log sample metadata before storing (should only contain orgId and documentId)
    if chunks:
        logger.info(f"Sample chunk metadata before storing (cleaned): {chunks[0].metadata}")
    
    vectorstore.add_documents(chunks)


def process_all_pdfs(org_id: str, document_mappings: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Process all PDF files for the given organization with document ID mapping.
    
    Args:
        org_id: Organization identifier
        document_mappings: Optional mapping of filename to document ID
        
    Returns:
        Dict containing processing results
        
    Raises:
        BadRequestException: If processing fails
    """
    try:
        logger.info(f"Starting PDF processing for organization: {org_id}")
        
        # Step 1: Get PDF folder and load documents with metadata
        pdf_folder = _get_pdf_folder()
        
        if document_mappings:
            logger.info(f"Processing with document mappings: {document_mappings}")
            docs = _load_pdf_documents_with_metadata(pdf_folder, document_mappings)
        else:
            # Fallback to original method without document IDs
            logger.warning("Processing without document mappings - document IDs will not be included")
            docs = _load_pdf_documents(pdf_folder)
        
        if not docs:
            logger.info("No PDF documents found to process")
            return {
                "status": "success", 
                "message": "No documents to process", 
                "chunks_processed": 0,
                "documents_loaded": 0
            }
        
        logger.info(f"Loaded {len(docs)} document pages")
        
        # Step 2: Clean up processed files
        _cleanup_processed_files(pdf_folder)
        
        # Step 3: Split documents into chunks
        text_splitter = _create_text_splitter()
        all_chunks = text_splitter.split_documents(docs)
        
        logger.info(f"Created {len(all_chunks)} chunks from documents")
        
        # Log sample chunk metadata after splitting
        if all_chunks:
            logger.info(f"Sample chunk metadata after splitting: {all_chunks[0].metadata}")
        
        # Step 4: Add organization metadata (preserves existing metadata including documentId)
        chunks_with_metadata = _add_organization_metadata(all_chunks, org_id)
        
        # Step 5: Store in vector database
        _store_chunks_in_vectorstore(chunks_with_metadata)
        
        logger.info(f"Successfully processed {len(chunks_with_metadata)} chunks for organization {org_id}")
        
        return {
            "status": "success",
            "message": f"Processed {len(chunks_with_metadata)} chunks",
            "chunks_processed": len(chunks_with_metadata),
            "documents_loaded": len(docs)
        }
        
    except Exception as e:
        logger.error(f"Error processing PDFs for organization {org_id}: {str(e)}")
        raise BadRequestException(f"Error in processing PDF: {str(e)}")       



