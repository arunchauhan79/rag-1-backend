from fastapi import APIRouter, Depends, status
from core import BadRequestException
from schema import OrganizationCreate, OrganizationUpdate, StandardResponse, OrganizationOutput
from controllers import createOrg, getOrganizations, get_organization_by_id, updateOrganization, delete_organization_by_id
from typing import List
from db import get_database
from pymongo.asynchronous.database import AsyncDatabase
from dependencies import require_admin

router = APIRouter()


@router.post('/', response_model=StandardResponse,status_code=status.HTTP_201_CREATED)
async def create_org(org:OrganizationCreate, db:AsyncDatabase = Depends(get_database)):
    try:        
        data = await createOrg(org,  db)  
        return StandardResponse(
            status="success",
            message="Organization created successfully",
            data=data
        )
    except Exception as e:
        raise BadRequestException(f"Error in creating Organization {e}")
    
    


@router.get('/', response_model=StandardResponse[List[OrganizationOutput]], status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def get_all_organization(db: AsyncDatabase = Depends(get_database)):
    try:    
        orgs = await getOrganizations(db)
        return StandardResponse(
            status="success",
            message="Organizations fetched successfully",
            data=orgs
        )
    except Exception as e:
     raise BadRequestException(f"Error in getting Organizations {e}")
 
 
 
@router.get('/{orgId}', response_model=StandardResponse[OrganizationOutput], status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def get_org_by_id(orgId:str, db: AsyncDatabase = Depends(get_database)):
    try:    
        org = await get_organization_by_id(orgId, db)
        return StandardResponse(
            status="success",
            message="Organization retrieved successfully",
            data=org
        )    
    except Exception as e:
        raise BadRequestException(f"Error in creating Organization by Id {e}")
    
            
    
@router.put('/', response_model=StandardResponse[OrganizationOutput], status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def update_organization(org:OrganizationUpdate, db: AsyncDatabase = Depends(get_database)):
    
    try:
        updated_org  = await updateOrganization(org, db)
        return StandardResponse(
            status="success",
            message="Organization updated successfully",
            data=updated_org
        )
    except Exception as e:
        raise BadRequestException(f"Error in updating Organization {e}")
    
    
    
@router.delete('/',status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def delete_organization(orgId:str, db: AsyncDatabase = Depends(get_database)):
    try:
        result = await delete_organization_by_id(orgId, db)
        return StandardResponse(
            status="success",
            message=result["message"],
            data=None
        )
    except Exception as e:
        raise BadRequestException(f"Error in deleting Organization {e}")

