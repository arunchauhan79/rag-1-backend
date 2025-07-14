from fastapi import FastAPI, Depends
from api import org_router,user_router, auth_router, doc_router
from db import get_database, close_db_connection
from pymongo.asynchronous.database import AsyncDatabase
from core import AppBaseException, app_base_exception_handler, DatabaseConnectionException

app = FastAPI()

app.add_exception_handler(AppBaseException, app_base_exception_handler)

@app.on_event("startup")
async def startup_event():
    """
    Automatically runs when FastAPI starts, even with Uvicorn.
    """
    try:
        db = get_database()
        if db is not None:
            print(f"✅ Connected to database: {db.name}")
        else:
            raise DatabaseConnectionException(f"Failed to connect to the database.")
    except Exception as e:
            raise DatabaseConnectionException(f"Startup error.")
        
    finally:
        await close_db_connection()


@app.get("/health")
async def health_check(db:AsyncDatabase = Depends(get_database)):
    try:        
        return {"status": "ok"}
    except Exception:
        raise DatabaseConnectionException(f"MongoDB is not reachable")
    finally:
        await close_db_connection()

app.include_router(org_router, prefix='/organization' ,tags=["Organization"])
app.include_router(user_router, prefix='/user' ,tags=["Users"])
app.include_router(auth_router, prefix="/auth" ,tags=["Authentication"])
app.include_router(doc_router, prefix="/doc", tags=["Docs"])