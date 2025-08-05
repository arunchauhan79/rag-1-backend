from fastapi import Response, APIRouter, Depends
from controllers import authenticateUser
from schema import LoginRequest
from pymongo.asynchronous.database import AsyncDatabase
from db import get_database

from schema import UserCreate,UserOutput,UserUpdate,StandardResponse





router = APIRouter()


@router.post('/login')
async def login(login:LoginRequest,response: Response, db:AsyncDatabase = Depends(get_database)):
    result =await authenticateUser(login, db)
    
    response.set_cookie(
        key="access_token",
        value=result["token"],
        httponly=True,
        secure=False,  # set True in production
        samesite="strict",
        max_age=86400,  # 1 day in seconds
    )
    
    return StandardResponse(
        status="success",
        message="User authenticated successfully",
        data=result
    )
    


@router.post("/logout", response_model=StandardResponse)
async def logout_user(response: Response):
    # Clear the cookie by setting it to empty and expiring it
    response.delete_cookie("access_token")
    return StandardResponse(
        status="success",
        message="User logged out successfully"
    )
    





