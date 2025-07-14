from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from schema import OrgCreate, OrgUpdate, StandardResponse
from controllers import createOrg, getOrganizations, get_organization_by_id, updateOrganization, delete_organization_by_id
from typing import Dict
from db import get_database
from pymongo.asynchronous.database import AsyncDatabase

router = APIRouter()


@router.post('/', response_model=StandardResponse,status_code=status.HTTP_201_CREATED)
async def create_org(org:OrgCreate, db:AsyncDatabase = Depends(get_database)):    
    org_id = await createOrg(org,  db)
    # return JSONResponse(
    #     status_code=status.HTTP_201_CREATED,
    #     content={
    #         "status":"success",
    #         "message":"Organization created successfully",
    #         "data":{"id":str(org_id)}
    #     }
    # )
    
    return StandardResponse(
        status="success",
        message="Organization created successfully",
        data={"id": str(org_id)}
      )



@router.get('/', response_model=StandardResponse)
async def get_all_organization(db: AsyncDatabase = Depends(get_database)):
    orgs = await getOrganizations(db)
    return StandardResponse(
        status="success",
        message="Organizations fetched successfully",
        data=orgs
    )

@router.get('/{orgId}', response_model=StandardResponse)
async def get_org_by_id(orgId:str, db: AsyncDatabase = Depends(get_database)):
    org = await get_organization_by_id(orgId, db)
    return StandardResponse(
        status="success",
        message="Organization retrieved successfully",
        data=org
    )
    
@router.put('/', response_model=StandardResponse)
async def update_organization(org:OrgUpdate, db: AsyncDatabase = Depends(get_database)):
    updated_org  = await updateOrganization(org, db)
    return StandardResponse(
        status="success",
        message="Organization updated successfully",
        data=updated_org
    )

@router.delete('/')
async def delete_organization(orgId:str, db: AsyncDatabase = Depends(get_database)):
    result = await delete_organization_by_id(orgId, db)
    return StandardResponse(
        status="success",
        message=result["message"],
        data=None
    )


