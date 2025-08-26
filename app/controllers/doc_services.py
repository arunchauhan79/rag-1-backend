import os
import time
from datetime import datetime
from typing import List, Dict, Any
from fastapi import UploadFile
from pymongo.asynchronous.database import AsyncDatabase
from bson import ObjectId
from core import logger, BadRequestException
from schema import DocumentUploadResponse, ProcessingResult, DocOutput, DocumentDeletionResponse, DocumentDeletionErrors
from rag1.main import process_all_pdfs
from utils import get_vectorstore

async def upload_files(
    files: List[UploadFile],
    organizationId: str,
    fileName:str,
    db: AsyncDatabase 
) -> DocumentUploadResponse:
    """
    Upload files and process them for the given organization.
    
    Args:
        files: List of files to upload
        organizationId: Organization ID
        db: Database connection
        
    Returns:
        DocumentUploadResponse with upload and processing results
    """
    upload_start_time = time.time()
    try:
        if not files:
            raise BadRequestException("No files provided for upload")
        
        if not organizationId:
            raise BadRequestException("Organization ID is required")

        UPLOAD_DIR = "uploaded_files"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        documents_to_insert = []
        errors = []

        logger.info(f"Starting upload of {len(files)} files for organization {organizationId}")

        # Process each file
        for file in files:
            try:
                # Validate file
                if not file.filename:
                    errors.append(f"File must have a filename")
                    continue
                    
                if file.content_type != "application/pdf":
                    errors.append(f"Invalid file type for '{file.filename}'. Only PDF files are allowed.")
                    continue

                # Generate unique filename
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                unique_filename = f"{organizationId}_{timestamp}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, unique_filename)

                # Save the file
                content = await file.read()
                if len(content) == 0:
                    errors.append(f"File '{file.filename}' is empty")
                    continue
                    
                with open(file_path, "wb") as f:
                    f.write(content)

                doc = {
                    "organizationId": organizationId,
                    "name": fileName,
                    "unique_filename": unique_filename,
                    "path": file_path,
                    "file_size": len(content),
                    "uploadedAt": datetime.utcnow(),
                    "status": "uploaded"
                }

                documents_to_insert.append(doc)
                logger.info(f"Prepared file for upload: {file.filename} ({len(content)} bytes)")
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                errors.append(f"Error processing file {file.filename}: {str(e)}")
        
        # Insert into MongoDB and create document mapping
        inserted_ids = []
        document_mappings = {}  # Map unique_filename to document ID
        
        if documents_to_insert:
            try:
                result = await db.documents.insert_many(documents_to_insert)
                print("Upload files result",result)
                inserted_ids = result.inserted_ids
                
                # Create mapping between unique_filename and document ID
                for i, doc in enumerate(documents_to_insert):
                    if i < len(inserted_ids):
                        document_mappings[doc['unique_filename']] = str(inserted_ids[i])
                
                logger.info(f"Inserted {len(inserted_ids)} documents into database")
                logger.info(f"Created document mappings: {document_mappings}")
                
            except Exception as e:
                logger.error(f"Error inserting documents: {str(e)}")
                errors.append(f"Database insertion error: {str(e)}")
        
        # Process PDFs after successful upload with document mappings
        processing_result = ProcessingResult(
            status="skipped",
            message="No files to process",
            chunks_processed=0,
            documents_loaded=0
        )
        
        if documents_to_insert and document_mappings:
            try:
                process_start_time = time.time()
                # Pass document mappings to the processing function
                processing_response = process_all_pdfs(organizationId, document_mappings)
                processing_time = time.time() - process_start_time
                
                processing_result = ProcessingResult(
                    status=processing_response.get("status", "unknown"),
                    message=processing_response.get("message", "Processing completed"),
                    chunks_processed=processing_response.get("chunks_processed", 0),
                    documents_loaded=processing_response.get("documents_loaded", 0),
                    processing_time=processing_time
                )
                
                logger.info(f"PDF processing completed for organization {organizationId}")
                
            except Exception as e:
                logger.error(f"Error processing PDFs: {str(e)}")
                processing_result = ProcessingResult(
                    status="failed",
                    message=f"PDF processing failed: {str(e)}",
                    chunks_processed=0,
                    documents_loaded=0,
                    error_details=str(e)
                )

        upload_time = time.time() - upload_start_time
        
        # Create response
        response = DocumentUploadResponse(
            success=len(documents_to_insert) > 0,
            files_uploaded=len(documents_to_insert),
            processing_result=processing_result,
            document_ids=[str(id) for id in inserted_ids] if inserted_ids else [],
            upload_time=upload_time,
            errors=errors if errors else []
        )
        
        logger.info(f"Upload completed: {len(documents_to_insert)} files uploaded, {len(errors)} errors")
        return response

    except Exception as e:
        logger.error(f"Error in upload_files: {str(e)}")
        
        # Return error response
        return DocumentUploadResponse(
            success=False,
            files_uploaded=0,
            processing_result=ProcessingResult(
                status="failed",
                message=f"Upload failed: {str(e)}",
                chunks_processed=0,
                documents_loaded=0,
                error_details=str(e)
            ),
            document_ids=[],
            upload_time=time.time() - upload_start_time,
            errors=[str(e)]
        )

async def getDocsByOrgId(orgId: str, db: AsyncDatabase) -> List[DocOutput]:
    """Get all documents for an organization."""
    try:
        logger.info(f"Fetching documents for organization: {orgId}")
        
        documents_cursor = db.documents.find({"organizationId": orgId})
        documents = []
        
        async for doc in documents_cursor:
            doc_output = DocOutput.model_validate({
                **doc,
                "id": str(doc["_id"]),
            })
            documents.append(doc_output)
        
        logger.info(f"Found {len(documents)} documents for organization {orgId}")
        return documents
        
    except Exception as e:
        logger.error(f"Error fetching documents for organization {orgId}: {str(e)}")
        raise BadRequestException(f"Error fetching documents: {str(e)}")
    
    
async def deleteDocuments(documentIds: List[str], db: AsyncDatabase) -> DocumentDeletionResponse:
    """
    Delete documents from MongoDB, remove physical files, and delete embeddings from Pinecone.
    
    Args:
        documentIds: List of document IDs to delete
        db: Database connection
        
    Returns:
        Dict containing deletion results
    """
    try:
        logger.info(f"Starting deletion of {len(documentIds)} documents")
        
        if not documentIds:
            raise BadRequestException("No document IDs provided for deletion")
        
        # Convert string IDs to ObjectIds and validate
        object_ids = []
        invalid_ids = []
        
        for doc_id in documentIds:
            if ObjectId.is_valid(doc_id):
                object_ids.append(ObjectId(doc_id))
            else:
                invalid_ids.append(doc_id)
        
        if invalid_ids:
            logger.warning(f"Invalid document IDs found: {invalid_ids}")
        
        if not object_ids:
            raise BadRequestException("No valid document IDs provided")
        
        # Step 1: Fetch documents from MongoDB to get file paths and metadata
        documents_to_delete = []
        async for doc in db.documents.find({"_id": {"$in": object_ids}}):
            documents_to_delete.append(doc)
        
        if not documents_to_delete:
            raise BadRequestException("No documents found with the provided IDs")
        
        logger.info(f"Found {len(documents_to_delete)} documents to delete")
        
        # Step 2: Delete physical files from filesystem
        deleted_files = []
        file_deletion_errors = []
        
        for doc in documents_to_delete:
            file_path = doc.get('path')
            unique_filename = doc.get('unique_filename')
            
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    logger.info(f"Deleted physical file: {file_path}")
                except Exception as e:
                    error_msg = f"Failed to delete file {file_path}: {str(e)}"
                    file_deletion_errors.append(error_msg)
                    logger.error(error_msg)
            else:
                logger.warning(f"File not found or no path specified: {file_path}")
        
        # Step 3: Delete embeddings from Pinecone vectorstore
        vectorstore_deletion_errors = []
        deleted_embeddings_count = 0
        
        try:
            vectorstore = get_vectorstore()
            
            # Delete embeddings based on document IDs
            for doc in documents_to_delete:
                doc_id_str = str(doc['_id'])
                try:
                    # Delete vectors by metadata filter
                    # Note: This depends on your vectorstore implementation
                    # For Pinecone, we need to delete by IDs that contain the documentId
                    vectorstore.delete(filter={"documentId": doc_id_str})
                    deleted_embeddings_count += 1
                    logger.info(f"Deleted embeddings for document ID: {doc_id_str}")
                except Exception as e:
                    error_msg = f"Failed to delete embeddings for document {doc_id_str}: {str(e)}"
                    vectorstore_deletion_errors.append(error_msg)
                    logger.error(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to connect to vectorstore: {str(e)}"
            vectorstore_deletion_errors.append(error_msg)
            logger.error(error_msg)
        
        # Step 4: Delete documents from MongoDB
        mongodb_deletion_result = await db.documents.delete_many({"_id": {"$in": object_ids}})
        deleted_from_mongodb = mongodb_deletion_result.deleted_count
        
        logger.info(f"Deleted {deleted_from_mongodb} documents from MongoDB")
        
        # Step 5: Prepare response summary
        success = deleted_from_mongodb > 0
        
        result = DocumentDeletionResponse(
            success=success,
            documents_requested=len(documentIds),
            documents_found=len(documents_to_delete),
            documents_deleted_from_mongodb=deleted_from_mongodb,
            physical_files_deleted=len(deleted_files),
            embeddings_deleted=deleted_embeddings_count,
            deleted_document_ids=[str(doc['_id']) for doc in documents_to_delete],
            deleted_file_paths=deleted_files,
            errors=DocumentDeletionErrors(
                invalid_ids=invalid_ids,
                file_deletion_errors=file_deletion_errors,
                vectorstore_deletion_errors=vectorstore_deletion_errors
            )
        )
        
        logger.info(f"Document deletion completed: {result.model_dump()}")
        return result
        
    except Exception as e:
        logger.error(f"Error in deleting documents: {str(e)}")
        raise BadRequestException(f"Error in deleting documents: {str(e)}")