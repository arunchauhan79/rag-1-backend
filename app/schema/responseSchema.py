from pydantic import BaseModel
from typing import Any, Optional

class StandardResponse(BaseModel):
    status: str  # "success" or "error"
    message: str
    data: Optional[Any] = None
