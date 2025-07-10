from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Annotated



class OrgModel(BaseModel):
    name:Annotated[str, Field(...,max_length=100,description="Name of the organization")]
    username:Annotated[str,Field(...,min_length=3
                                 ,description="Unique username of Organization")]
    email:Annotated[EmailStr,Field(...,min_length=3,description="Email Id of the organization")]
    createAt:datetime
    