import os
from fastapi import UploadFile
from schema import StandardResponse, DocOutput
from pymongo.asynchronous.database import AsyncDatabase
from core import BadRequestException, DatabaseQueryException, logger
from datetime import datetime
from typing import List, Dict, Any
from rag1 import process_all_pdfs



async def upload_files(
    files: List[UploadFile],
    organizationId: str,
    db: AsyncDatabase 
) -> dict:
    """
    Upload PDF files and process them for the organization.
    
    Args:
        files: List of uploaded files
        organizationId: Organization identifier
        db: Database connection
        
    Returns:
        Dict with upload and processing results
        
    Raises:
        BadRequestException: If upload or validation fails
    """
    try:
        if not files:
            raise BadRequestException("No files provided for upload")
        
        if not organizationId:
            raise BadRequestException("Organization ID is required")

        UPLOAD_DIR = "uploaded_files"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        documents_to_insert = []

        logger.info(f"Starting upload of {len(files)} files for organization {organizationId}")

        for file in files:
            # Validate file
            if not file.filename:
                raise BadRequestException("File must have a filename")
                
            if file.content_type != "application/pdf":
                raise BadRequestException(
                    f"Invalid file type for '{file.filename}'. Only PDF files are allowed."
                )

            # Generate unique filename with better timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            unique_filename = f"{organizationId}_{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            # Save the file
            content = await file.read()
            if len(content) == 0:
                raise BadRequestException(f"File '{file.filename}' is empty")
                
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
        
         # Insert into MongoDB
        inserted_ids = []
        if documents_to_insert:
            result = await db.documents.insert_many(documents_to_insert)
            inserted_ids = result.inserted_ids
            logger.info(f"Inserted {len(inserted_ids)} documents into database")
           
        # Process PDFs after successful upload
        try:
            processing_result = process_all_pdfs(organizationId)
            logger.info(f"PDF processing completed: {processing_result}")
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            # Don't fail the upload if processing fails - files are already uploaded
            processing_result = {"status": "error", "message": str(e)}

        return {
            "success": True,
            "files_uploaded": len(files),
            "processing_result": processing_result,
            "document_ids": [str(id) for id in inserted_ids] if inserted_ids else []
        }

    except Exception as e:
        raise BadRequestException(f"Error in uploading files: {str(e)}")

async def getDocsByOrgId(orgId: str, db: AsyncDatabase) -> List[DocOutput]:
    """
    Retrieve all documents for a specific organization.
    
    Args:
        orgId: Organization identifier
        db: Database connection
        
    Returns:
        List of documents for the organization
        
    Raises:
        DatabaseQueryException: If database query fails
    """
    try:
        if not orgId:
            raise BadRequestException("Organization ID is required")
            
        logger.info(f"Fetching documents for organization: {orgId}")
        
        docs_cursor = db.documents.find({"organizationId": orgId})
        docs = []
        
        async for doc in docs_cursor:
            try:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                docs.append(DocOutput.model_validate(doc))
            except Exception as validation_error:
                logger.warning(f"Failed to validate document {doc.get('id', 'unknown')}: {validation_error}")
                continue
        
        logger.info(f"Retrieved {len(docs)} documents for organization {orgId}")
        return docs

    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch documents for organization {orgId}: {str(e)}")
        raise DatabaseQueryException(f"Failed to get documents: {str(e)}")

