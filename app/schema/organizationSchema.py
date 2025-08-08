from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from datetime import datetime 
from typing import Annotated
from bson import ObjectId


PyObjectId = Annotated[str, BeforeValidator(str)]

class OrganizationBase(BaseModel):
    name:Annotated[str, Field(...,max_length=100,description="Name of the organization")]
    username:Annotated[str,Field(...,min_length=3
                                 ,description="Unique username of Organization")]
    email:Annotated[EmailStr,Field(...,min_length=3,description="Email Id of the organization")]    
    
class OrganizationCreate(OrganizationBase):
    password:Annotated[str,Field(...,min_length=4, max_length=16, description="Organization password, with that organization will be able to login.")]
    
    
class OrganizationUpdate(BaseModel):
    id:Annotated[PyObjectId,Field(default_factory=PyObjectId ,alias="id", description="Unique id of the organization")]  
    name:Annotated[str, Field(...,max_length=100,description="Name of the organization")]
        
    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
    
    
class OrganizationModel(OrganizationBase):    
    createAt:datetime
    

class OrganizationOutput(OrganizationModel):
    id:Annotated[PyObjectId ,Field(default_factory=PyObjectId ,alias="_id", description="Unique id of the organization")]  
    
    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
    