from fastapi import APIRouter, Depends
from schema import OrgCreate
from controllers import createOrg,getOrganizations, get_organization_by_id
from typing import Dict
from db import get_database
from pymongo.asynchronous.database import AsyncDatabase

router = APIRouter()


@router.post('/')
async def create_org(org:OrgCreate, db:AsyncDatabase = Depends(get_database)):    
    org_id = await createOrg(org,  db)
    return {"id":str(org_id),"message":"Organization created"}


@router.get('/')
async def get_all_organization(db: AsyncDatabase =Depends(get_database)):
    orgs = await getOrganizations(Depends(get_database))
    return orgs

@router.get('/{orgId}')
async def get_org_by_id(orgId:str):
    org = await get_organization_by_id(orgId)
    return org
    




