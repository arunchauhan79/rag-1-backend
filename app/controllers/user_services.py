from typing import Dict, List
from schema import UserCreate, UserUpdate, UserOutput, UserModel
from fastapi import HTTPException
from core import UserAlreadyExistsException, NotModifiedException, DatabaseQueryException,NotFoundException, BadRequestException, hash_password, verify_password,UnauthorizedException
from pymongo.errors import PyMongoError
from pymongo.asynchronous.database import AsyncDatabase
from datetime import datetime, timezone
from bson import ObjectId


async def createUser(user:UserCreate, db:AsyncDatabase) -> UserOutput:
    try:
        if db is None:
            raise DatabaseConnectionException(f"Database not connected")
        # Check for existing username/email
        if await db.users.find_one({"username": user.username}):
            raise UserAlreadyExistsException(f"User with username '{user.username}' already exists")

        if await db.organizations.find_one({"email": user.email}):
            raise UserAlreadyExistsException(f"User with email '{user.email}' already exists")

        hashed_pwd = hash_password(user.password)
        user_document = UserModel(
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            username=user.username,
            password=hashed_pwd,
            organizationId=user.organizationId,            
            role=user.role,
            createdAt=datetime.now(timezone.utc)
        ).model_dump()
        result = await db.users.insert_one(user_document)
        # if not result.inserted_id:
        #     raise DatabaseQueryException(f"Failed to create organization")

        return str(result.inserted_id)

        
    except Exception as e:    
        raise HTTPException(status_code=500,detail=f"Failed to create user: {e}",)
    
async def updateUser(userId: str, update_data: UserUpdate, db: AsyncDatabase) -> UserOutput:
    try:
        print("In updateUser")
        if not ObjectId.is_valid(userId):
            raise BadRequestException("Invalid user ID format")

        # Ensure user exists
        existing_user = await db.users.find_one({"_id": ObjectId(userId)})
        if not existing_user:
            raise NotFoundException("User not found")

        # Convert Pydantic model to dict
        data = update_data.model_dump(exclude_unset=True)
        data["updatedAt"] = datetime.now(timezone.utc)

        result = await db.users.update_one(
            {"_id": ObjectId(userId)},
            {"$set": data}
        )

        if result.modified_count == 0:
            raise NotModifiedException("No changes were made")

        # Fetch and return updated user
        updated_user = await db.users.find_one({"_id": ObjectId(userId)})
        return UserOutput.model_validate({
            **updated_user,
            "id": str(updated_user["_id"]),
        })

    except Exception as e:
        raise DatabaseQueryException(f"Failed to update user: {e}")
    
    
async def getUserById(userId: str, db: AsyncDatabase) -> UserOutput:
    try:
        if not ObjectId.is_valid(userId):
            raise BadRequestException(status_code=400, detail="Invalid user ID format")

        user = await db.users.find_one({"_id": ObjectId(userId)})
        if not user:
            raise NotFoundException(status_code=404, detail="User not found")

        return UserOutput.model_validate({**user,"id": str(user["_id"])})
    except Exception as e:
        raise DatabaseQueryException(status_code=500, detail=f"Failed to get user details: {e}")
   
async def getUsersByOrgId(orgId: str, db: AsyncDatabase) -> List[UserOutput]:
    try:
        users_cursor = db.users.find({"organizationId": orgId})
        users = []
        async for user in users_cursor:
            user["id"] = str(user["_id"])
            users.append(UserOutput.model_validate({**user, "_id": str(user["_id"])}))
        return users
    except Exception as e:
        raise DatabaseQueryException(status_code=500, detail=f"Failed to fetch users: {e}")
    
    


async def deleteUser(userId: str, db: AsyncDatabase) -> UserOutput:
    try:
        if not ObjectId.is_valid(userId):
            raise BadRequestException("Invalid user ID format")

        # Find existing user
        user = await db.users.find_one({"_id": ObjectId(userId)})
        if not user:
            raise NotFoundException("User not found")

        # Delete user
        result = await db.users.delete_one({"_id": ObjectId(userId)})

        if result.deleted_count == 0:
            raise DatabaseQueryException("Failed to delete user")

        # Return deleted user data as confirmation
        return UserOutput.model_validate({
            **user,
            "id": str(user["_id"]),
        })

    except Exception as e:
        raise DatabaseQueryException(f"Failed to delete user: {e}")

 
