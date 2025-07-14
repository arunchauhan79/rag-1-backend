import os
from fastapi import APIRouter,Depends, UploadFile, File
from dependencies import require_admin
from schema import StandardResponse
from pymongo.asynchronous.database import AsyncDatabase
from db import get_database
from core import BadRequestException
from datetime import datetime
from typing import List
from controllers import upload_files

router = APIRouter()





@router.post('/',response_model=StandardResponse, summary="Upload a PDF file", dependencies=[Depends(require_admin)])
async def upload_docs(
    files:List[UploadFile] = File(...),
    db:AsyncDatabase = Depends(get_database)
    
):
    result = await upload_files(files, db)
    
    return StandardResponse(
        status="success",
        message="Files uploaded successfully",
        data=result
    )