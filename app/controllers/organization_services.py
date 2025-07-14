from typing import List
from schema import OrgOutput, OrgCreate, OrgModel, OrgUpdate, UserModel
from datetime import datetime, timezone
from db.client import get_database
from fastapi import HTTPException, status, Depends
from pymongo.errors import PyMongoError
from pymongo.asynchronous.database import AsyncDatabase
from bson import ObjectId
from core import UserAlreadyExistsException, DatabaseConnectionException,DatabaseQueryException,NotFoundException,hash_password
import logging

logger = logging.getLogger(__name__)


async def createOrg(org_data: OrgCreate, db:AsyncDatabase) -> str:
    try:
        if db is None:
            raise DatabaseConnectionException(f"Database not connected")

        # Check for existing username/email
        if await db.organizations.find_one({"username": org_data.username}):
            raise UserAlreadyExistsException(f"Organization with username '{org_data.username}' already exists")

        if await db.organizations.find_one({"email": org_data.email}):
            raise UserAlreadyExistsException(f"Organization with email '{org_data.email}' already exists")

        # Build OrgModel and convert to dict
        org_document = OrgModel(
            name=org_data.name,
            username=org_data.username,
            email=org_data.email,
            createAt=datetime.now(timezone.utc)
        ).model_dump()

        org_result = await db.organizations.insert_one(org_document)
        
        
        if not org_result.inserted_id:
            raise DatabaseQueryException(f"Failed to create organization")

        hashed_pwd = hash_password(org_data.password)
        user_document = UserModel(
            firstname=org_data.name,
            lastname='',
            email=org_data.email,
            username=org_data.username,
            password=hashed_pwd,
            organizationId=str(org_result.inserted_id),            
            role="admin",
            createdAt=datetime.now(timezone.utc)
        ).model_dump()
        result = await db.users.insert_one(user_document)
        
        return str(org_result.inserted_id)

    except PyMongoError:
        logger.exception("Database error while creating organization")
        raise DatabaseConnectionException(f"Database error")
    except Exception as e:
        logger.exception("Unexpected error while creating organization")
        raise DatabaseConnectionException(f"Internal server error")


async def get_organization_by_id(org_id: str, db) -> OrgOutput:
    try:
        if db is None:
            raise DatabaseQueryException("Database not connected")
        org = await db.organizations.find_one({"_id": ObjectId(org_id)})
        if not org:
            raise NotFoundException("Organization not found")
        org["_id"] = str(org["_id"])
        return OrgOutput.model_validate(org, from_attributes=True)

    except Exception as e:
        logger.exception("Failed to fetch organization by ID")
        raise DatabaseQueryException(f"Failed to get organization details {e}")


async def get_org_by_name(name: str, db:AsyncDatabase = Depends(get_database)) -> OrgOutput:
    try:
        if db is None:
            raise DatabaseConnectionException("Database not connected")

        org = await db.organizations.find_one({"name": name})
        if not org:
            raise DatabaseQueryException("Organization not found")

        return OrgOutput.model_validate({**org, "_id": str(org["_id"])})
    
    except Exception as e:
        logger.exception("Failed to fetch organization by name")
        raise DatabaseQueryException("Internal server error")


async def getOrganizations(db:AsyncDatabase) -> List[OrgOutput]:
    try:
        cursor = db.organizations.find()
        orgs = []
        async for org in cursor:
            orgs.append(OrgOutput.model_validate({**org, "_id": str(org["_id"])}))
        return orgs
    except Exception as e:
        logger.exception("Failed to fetch organizations")
        raise DatabaseQueryException("Internal server error")


async def updateOrganization(org:OrgUpdate, db:AsyncDatabase) -> OrgOutput:
    try:
        existing_org = await get_organization_by_id(org.id,db)
        if existing_org is not None:
            await db.organizations.update_one({
                "_id":ObjectId(existing_org.id)
            },
            {"$set":{"name":org.name}})
            updated = await get_organization_by_id(existing_org.id, db)
            return updated
        else:
            raise NotFoundException("Organization not found")
        
        
    except Exception as e:
        raise DatabaseQueryException("Internal server error",e)
     
     
async def delete_organization_by_id(orgId:str,db:AsyncDatabase) -> dict:
    try:
        result = await db.organizations.delete_one({"_id":ObjectId(orgId)})
        
        if result.deleted_count == 0:
            raise NotFoundException("Orgazniation not found")
        
        return {"message":"Organization deleted successfully"}
        
    except Exception as e:
        raise DatabaseQueryException("Error in deleting organization")