from fastapi import APIRouter, Depends, status
from controllers import authenticateUser
from schema import LoginRequest
from pymongo.asynchronous.database import AsyncDatabase
from db import get_database
from core import settings, BadRequestException
from schema import StandardResponse





router = APIRouter()


@router.post('/login',response_model=StandardResponse,status_code=status.HTTP_200_OK)
async def login(login:LoginRequest,db:AsyncDatabase = Depends(get_database)):
    try:
        print("login",login)
        result = await authenticateUser(login, db)
        
        # response.set_cookie(
        #     key="access_token",
        #     value=result["token"],
        #     httponly=True,
        #     secure=False,  # set True in production
        #     samesite="strict",
        #     max_age=settings.token_expire_minutes,  # 1 day in seconds
        # )
        
        return StandardResponse(
            status="success",
            message="User authenticated successfully",
            data=result
        )
    except Exception as e:
        raise BadRequestException(f"Error in logging user {e}")


@router.post("/logout",status_code=status.HTTP_200_OK, response_model=StandardResponse)
async def logout_user(response: StandardResponse):
    # Clear the cookie by setting it to empty and expiring it
    try:
        response.delete_cookie("access_token")
        return StandardResponse(
            status="success",
            message="User logged out successfully",
            data=None
        )
    except Exception as e:
        raise BadRequestException(f"Error in logout user {e}")





