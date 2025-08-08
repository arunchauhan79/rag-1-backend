import os
from fastapi import APIRouter,Depends,status
from dependencies import require_admin
from schema import SearchBase, StandardResponse, QueryResponse
from pymongo.asynchronous.database import AsyncDatabase
from db import get_database
from core import BadRequestException
from controllers import query_doc

router = APIRouter()





@router.post('/query',response_model=StandardResponse[QueryResponse],status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def query(userSearch:SearchBase, db:AsyncDatabase = Depends(get_database)):
    try:        
        print("query_doc")
        result = await query_doc(userSearch.searchTxt,userSearch.orgId, db)
        print("result....",result)
        return StandardResponse(         
            status="success",
            message="Data fetched successfully",
            data=result
        )
    except Exception as e:
            raise BadRequestException(f"Error in querying {e}")  