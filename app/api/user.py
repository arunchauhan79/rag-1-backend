from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from schema import UserCreate,UserOutput,UserUpdate,StandardResponse
from controllers import createUser,updateUser,deleteUser, getUsersByOrgId, getUserById
from typing import Dict
from db import get_database
from pymongo.asynchronous.database import AsyncDatabase
from dependencies import require_admin

router = APIRouter()


@router.post('/', response_model=StandardResponse,status_code=status.HTTP_201_CREATED,  dependencies=[Depends(require_admin)])
async def create_user(user:UserCreate, db:AsyncDatabase = Depends(get_database)):    
    print("In create_user")
    user_id = await createUser(user,  db)
   
    
    return StandardResponse(
        status="success",
        message="User created successfully",
        data={"id": str(user_id)}
      )



@router.get('/{orgId}', response_model=StandardResponse)
async def get_users_by_OrgId(orgId:str, db: AsyncDatabase = Depends(get_database)):
    users = await getUsersByOrgId(orgId, db)
    return StandardResponse(
        status="success",
        message="Users fetched successfully",
        data=users
    )

@router.get('/user/{userId}', response_model=StandardResponse)
async def get_user_by_id(userId:str, db: AsyncDatabase = Depends(get_database)):
    user = await getUserById(userId, db)
    return StandardResponse(
        status="success",
        message="User retrieved successfully",
        data=user
    )
    
@router.put('/{userId}', response_model=StandardResponse)
async def update_user(userId:str , user:UserUpdate, db: AsyncDatabase = Depends(get_database)):
    updated_org  = await updateUser(userId, user, db)
    return StandardResponse(
        status="success",
        message="User updated successfully",
        data=updated_org
    )

@router.delete('/')
async def delete_user(userId:str, db: AsyncDatabase = Depends(get_database)):
    result = await deleteUser(userId, db)
    return StandardResponse(
        status="success",
        message="User deleted successfully",
        data=None
    )


