from fastapi import FastAPI, Depends, APIRouter
from api import org_router,user_router, auth_router, doc_router
from db import get_database, close_db_connection
from pymongo.asynchronous.database import AsyncDatabase
from core import AppBaseException, app_base_exception_handler, DatabaseConnectionException
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()


origins = [
    "http://localhost:3000",         # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:5173"
]

app.add_exception_handler(AppBaseException, app_base_exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # or ["*"] to allow all (dev only)
    allow_credentials=True,
    allow_methods=["*"],                # allow all HTTP methods
    allow_headers=["*"],                # allow all headers
)

api_router = APIRouter(prefix="/api")
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

api_router.include_router(org_router, prefix='/organization' ,tags=["Organization"])
api_router.include_router(user_router, prefix='/user' ,tags=["Users"])
api_router.include_router(auth_router, prefix="/auth" ,tags=["Authentication"])
api_router.include_router(doc_router, prefix="/doc", tags=["Docs"])

app.include_router(api_router)