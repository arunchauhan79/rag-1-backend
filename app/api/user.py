from fastapi import APIRouter, Depends, status
from typing import List
from schema import UserCreate,UserOutput,UserUpdate,StandardResponse,SearchBase
from controllers import createUser,updateUser,deleteUser, getUsersByOrgId, getUserById
from core import BadRequestException
from db import get_database
from pymongo.asynchronous.database import AsyncDatabase
from dependencies import require_admin

router = APIRouter()


@router.post('/', response_model=StandardResponse,status_code=status.HTTP_201_CREATED,  dependencies=[Depends(require_admin)])
async def create_user(user:UserCreate, db:AsyncDatabase = Depends(get_database)):    
    
    try:
        user_id = await createUser(user,  db)  
        
        return StandardResponse(
            status="success",
            message="User created successfully",
            data={"id": str(user_id)}
            )
    except Exception as e:
            raise BadRequestException(f"Error in creating User {e}")
        


@router.get('/{orgId}', response_model=StandardResponse[List[UserOutput]],status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def get_users_by_OrgId(orgId:str, db: AsyncDatabase = Depends(get_database)):
    try:
        users = await getUsersByOrgId(orgId, db)
        return StandardResponse(
            status="success",
            message="Users fetched successfully",
            data=users
        )
    except Exception as e:
                raise BadRequestException(f"Error in getting User {e}")
            
            
            
@router.get('/user/{userId}', response_model=StandardResponse[UserOutput],status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def get_user_by_id(userId:str, db: AsyncDatabase = Depends(get_database)):
    try:
        user = await getUserById(userId, db)
        return StandardResponse(
            status="success",
            message="User retrieved successfully",
            data=user
        )
    except Exception as e:
            raise BadRequestException(f"Error in getting User by Id {e}")
        
        
        
@router.put('/{userId}', response_model=StandardResponse[UserOutput], status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def update_user(userId:str , user:UserUpdate, db: AsyncDatabase = Depends(get_database)):
    try:
        updated_org  = await updateUser(userId, user, db)
        return StandardResponse(
            status="success",
            message="User updated successfully",
            data=updated_org
        )
    except Exception as e:
            raise BadRequestException(f"Error in updating User {e}")
        
        
@router.delete('/', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_user(userId:str, db: AsyncDatabase = Depends(get_database)):
    try:
        result = await deleteUser(userId, db)
        return None  # 204 responses should not have a body
    except Exception as e:
            raise BadRequestException(f"Error in deleting User {e}")
        
        



