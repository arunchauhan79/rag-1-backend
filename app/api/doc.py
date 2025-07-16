import os
from fastapi import APIRouter,Depends, UploadFile, File, Query
from dependencies import require_admin
from schema import StandardResponse
from pymongo.asynchronous.database import AsyncDatabase
from db import get_database
from core import BadRequestException
from datetime import datetime
from typing import List
from controllers import upload_files, getDocsByOrgId

router = APIRouter()





@router.post('/',response_model=StandardResponse, summary="Upload a PDF file", dependencies=[Depends(require_admin)])
async def upload_docs(
    files:List[UploadFile] = File(...),
    organizationId:str = Query(..., description="Organization ID"),
    db:AsyncDatabase = Depends(get_database)
    
):
    result = await upload_files(files, organizationId, db)
    
    return StandardResponse(
        status="success",
        message="Files uploaded successfully",
        data=result
    )
    

@router.get('/{orgId}', response_model=StandardResponse)
async def get_org_by_id(orgId:str, db: AsyncDatabase = Depends(get_database)):
    org = await getDocsByOrgId(orgId, db)
    return StandardResponse(
        status="success",
        message="Documents retrieved successfully",
        data=org
    )