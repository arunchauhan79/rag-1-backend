from fastapi import FastAPI, HTTPException, APIRouter



router = APIRouter()

@router.post('/user')
async def create_user():
    pass