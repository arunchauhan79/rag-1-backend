from pydantic import BaseModel
from typing import Any, Optional, TypeVar, Generic

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    status: str  # "success" or "error"
    message: str
    data: Optional[T] = None
    
    class Config:
        arbitrary_types_allowed = True

class ProcessPDFResponse(BaseModel):
    status: str
    message: str
    chunks_processed: int
    documents_loaded: int
    
    class Config:
        arbitrary_types_allowed = True

# Non-generic version for simple cases
class SimpleResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None
    
    class Config:
        arbitrary_types_allowed = True