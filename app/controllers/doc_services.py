import os
import time
from datetime import datetime
from typing import List, Dict, Any
from fastapi import UploadFile
from pymongo.asynchronous.database import AsyncDatabase
from core import logger, BadRequestException
from schema import DocumentUploadResponse, ProcessingResult, DocOutput
from rag1.main import process_all_pdfs

async def upload_files(
    files: List[UploadFile],
    organizationId: str,
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
                    "name": file.filename,
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
        
        # Insert into MongoDB
        inserted_ids = []
        if documents_to_insert:
            try:
                result = await db.documents.insert_many(documents_to_insert)
                inserted_ids = result.inserted_ids
                logger.info(f"Inserted {len(inserted_ids)} documents into database")
            except Exception as e:
                logger.error(f"Error inserting documents: {str(e)}")
                errors.append(f"Database insertion error: {str(e)}")
        
        # Process PDFs after successful upload
        processing_result = ProcessingResult(
            status="skipped",
            message="No files to process",
            chunks_processed=0,
            documents_loaded=0
        )
        
        if documents_to_insert:
            try:
                process_start_time = time.time()
                processing_response = process_all_pdfs(organizationId)
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