from typing import Dict, List
from db.client import DATABASE_NAME
from schema.organizationSchema import OrgOutput
from schema.userSchema import UserOutput
from fastapi import HTTPException
from pymongo.errors import PyMongoError
import bcrypt

def create_user(user:Dict) -> OrgOutput:
    try:
        result = DATABASE_NAME.users.insert_one(user.dict())
        return OrgOutput(result)
        
    except Exception as e:    
        raise HTTPException(status_code=500,detail="Failed to create user")
    
    

def get_user_by_id(userId:str) -> UserOutput:
    try:
        user = DATABASE_NAME.users.find_one({id:userId})
        return UserOutput(user)
    
    except Exception as e:
        raise HTTPException(status_code=500, details="Failed to get user details")
    
def get_users(orgId: str) -> List[UserOutput]:
    try:
        users_cursor = DATABASE_NAME.users.find({"organizationId": orgId})
        users = [UserOutput(**user) for user in users_cursor]
        return users

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error while fetching users")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user details")
    
    
def authenticate_user(email:str, password:str) -> 8:
    try:
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        user = DATABASE_NAME.users.find_one({"email":email})
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not bcrypt.checkpw(password.encode(), user['password'].encode()):
            raise HTTPException(status_code=401, detail="Invalid email and password")
        
        user.pop("password",None)
        return UserOutput(**user)
             
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error in authenticate user")