from pydantic import BaseModel, Field,EmailStr , BeforeValidator
from typing import Annotated, Optional, Literal, List
from datetime import datetime
from bson import ObjectId
     
     
PyObjectId = Annotated[str, BeforeValidator(str)]


class UserBase(BaseModel):
    username: Annotated[str, Field(..., max_length=100,
                                   description="Unique username of user which will be used to login in application",
                                   examples=["user1"])]
    firstname: Annotated[str, Field(..., max_length=100,
                                   description="First name of the user",
                                   examples=["John"])]
    lastname: Annotated[Optional[str], Field(..., max_length=100,
                                             description="Last name of the user",
                                             examples=["Doe"])]
    email: Annotated[EmailStr, Field(..., description="Email Id of the user",
                                     examples=["example@gmail.com"])]
    password: Annotated[str, Field(..., min_length=6,
                                   description="Password to login in application")]
    organizationId: Annotated[PyObjectId, Field(..., description="Id of the user's organization")]
    role: Annotated[Optional[Literal["admin", "user", "org"]],
                    Field(default="user", description="Which role user will have",
                          examples=["user"])]

class UserCreate(UserBase):
    createdAt:Annotated[datetime,Field(...,description="Date when user has created")]
    
class UserUpdate(BaseModel):  
    firstname:Annotated[str,Field(...,max_length=100,
                                 description="First name of the user",
                                 examples=["John"]
                                 )]
    lastname:Annotated[Optional[str],Field(...,max_length=100,
                                 description="Last name of the user",
                                 examples=["Doe"]
                                 )]

    
    
class UserOutput(UserBase):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id",
                                    description="Unique id of user",
                                    examples=["64c21ffb7b1234567890abcd"])]
    password: str = Field(exclude=True)
    createdAt: Annotated[datetime, Field(..., description="Date when user has created")]

    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True

class UserModel(UserBase):
    createdAt:datetime
    
