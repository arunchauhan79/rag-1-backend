from pydantic import BaseModel, Field,EmailStr
from typing import Annotated, Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    username:Annotated[str,Field(...,max_length=100,
                                 description="Unique username of user which will be used to login in application",
                                 examples=["user1"]
                                 )]
    firstname:Annotated[str,Field(...,max_length=100,
                                 description="First name of the user",
                                 examples=["John"]
                                 )]
    lastname:Annotated[Optional[str],Field(...,max_length=100,
                                 description="Last name of the user",
                                 examples=["Doe"]
                                 )]
    email:Annotated[EmailStr,Field(...,description="Email Id of the user",
                                 examples=["example@gmail.com"]
                                 )]
    password:Annotated[str,Field(...,min_length=6,
                                 description="Password to login in application")]
                                 
    organizationId:Annotated[str,Field(...,max_length=100,
                                 description="Id of the user's organization",                                 
                                 )]
    role:Annotated[Optional[Literal["admin","user","org"]],Field(default="user",description="Which role user will have",
                                 examples=["user"]
                                 )]

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
    id:Annotated[str,Field(...,  description="Unique id of user",
                                 examples=["usj1kj2n3kj12312-1231k23-123k123er1"]
                                 )]   
    password:str = Field(exclude=True)
    createdAt:Annotated[datetime,Field(...,description="Date when user has created")]
    

class UserModel(UserBase):
    createdAt:datetime