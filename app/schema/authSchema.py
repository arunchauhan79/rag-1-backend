from pydantic import BaseModel, Field
from typing import Annotated


class Token(BaseModel):
    access_token: Annotated[str,Field(...,description="Access token which will be use for user to authenticate")]
    token_type: Annotated[str,Field(...,description="Type of Access token")]
    
    
class LoginRequest(BaseModel):
    username: Annotated[str,Field(...,description="Username of the user")]
    password: Annotated[str, Field(..., description="password of the user")]    
