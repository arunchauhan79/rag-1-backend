from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from typing import List
from schema import DocumentUploadResponse, StandardResponse, DocOutput
from controllers import upload_files, getDocsByOrgId
from core import BadRequestException
from db import get_database
from pymongo.asynchronous.database import AsyncDatabase
from dependencies import require_admin

router = APIRouter()

@router.post('/upload', response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def upload_documents(
    files: List[UploadFile] = File(...),
    organizationId: str = Form(...),
    db: AsyncDatabase = Depends(get_database)
):
    """
    Upload PDF documents for an organization.
    
    Args:
        files: List of PDF files to upload
        organizationId: Organization ID
        db: Database connection
        
    Returns:
        DocumentUploadResponse with upload and processing results
    """
    try:
        result = await upload_files(files, organizationId, db)
        return result
    except Exception as e:
        raise BadRequestException(f"Error uploading files: {e}")

@router.get('/documents/{orgId}', response_model=StandardResponse[List[DocOutput]], status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def get_documents_by_org(orgId: str, db: AsyncDatabase = Depends(get_database)):
    """Get all documents for an organization."""
    try:
        documents = await getDocsByOrgId(orgId, db)
        return StandardResponse(
            status="success",
            message=f"Retrieved {len(documents)} documents",
            data=documents
        )
    except Exception as e:
        raise BadRequestException(f"Error retrieving documents: {e}")