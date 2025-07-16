import os
from fastapi import  UploadFile
from schema import StandardResponse, DocOutput
from pymongo.asynchronous.database import AsyncDatabase
from core import BadRequestException, DatabaseQueryException, logger
from datetime import datetime
from typing import List



async def upload_files(
    files: List[UploadFile],
    organizationId: str,
    db: AsyncDatabase 
) -> List[dict]:
    try:
        UPLOAD_DIR = "uploaded_files"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        documents_to_insert = []

        for file in files:
            # Validate file type
            if file.content_type != "application/pdf":
                raise BadRequestException(
                    f"Invalid file type for '{file.filename}'. Only PDF files are allowed."
                )

            # Generate unique filename
            timestamp = datetime.utcnow().isoformat().replace(":", "-")
            unique_filename = f"{organizationId}_{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            # Save the file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            doc = {
                "organizationId": organizationId,
                "name": file.filename,
                "unique_filename": unique_filename,
                "path": file_path,
                "uploadedAt": datetime.utcnow()
            }

            documents_to_insert.append(doc)

        # Insert into DB
        if documents_to_insert:
            insert_result = await db.documents.insert_many(documents_to_insert)


        return documents_to_insert

    except Exception as e:
        raise BadRequestException(f"Error in uploading files: {str(e)}")

async def getDocsByOrgId(orgId: str, db) -> DocOutput:
    try:
        docs_cursor = db.documents.find({"organizationId": orgId})
        docs = []
        async for doc in docs_cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            docs.append(DocOutput.model_validate(doc))
        return docs

    except Exception as e:
        logger.exception("Failed to fetch Documents by OrganizationId")
        raise DatabaseQueryException(f"Failed to get Documents details {e}")

