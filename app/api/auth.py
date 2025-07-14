from fastapi import FastAPI, APIRouter, Depends
from controllers import authenticateUser
from schema import LoginRequest
from pymongo.asynchronous.database import AsyncDatabase
from db import get_database

from schema import UserCreate,UserOutput,UserUpdate,StandardResponse





router = APIRouter()


@router.post('/')
async def login(login:LoginRequest, db:AsyncDatabase = Depends(get_database)):
    result =await authenticateUser(login, db)
    print("login result",result)
    return StandardResponse(
        status="success",
        message="User authenticated successfully",
        data=result
    )
    





