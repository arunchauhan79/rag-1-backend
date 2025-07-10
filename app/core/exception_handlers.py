from fastapi.requests import Request
from fastapi.responses import JSONResponse
from .exceptions import AppBaseException
import logging

logger = logging.getLogger("uvicorn.error")

async def app_base_exception_handler(request: Request, exc: AppBaseException):
    # Log the error
    logger.error(f"[{exc.status_code}] {exc.error_code}: {exc.detail} - Path: {request.url.path}")
    
    # Return custom response
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.detail
        }
    )
