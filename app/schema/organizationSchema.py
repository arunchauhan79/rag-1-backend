from pydantic import BaseModel, Field, EmailStr
from datetime import datetime 
from typing import Annotated



class OrgBase(BaseModel):
    name:Annotated[str, Field(...,max_length=100,description="Name of the organization")]
    username:Annotated[str,Field(...,min_length=3
                                 ,description="Unique username of Organization")]
    email:Annotated[EmailStr,Field(...,min_length=3,description="Email Id of the organization")]    
    
class OrgCreate(OrgBase):
    password:Annotated[str,Field(...,min_length=4, max_length=16, description="Organization password, with that organization will be able to login.")]
    
    
    
class OrgModel(OrgBase):    
    createAt:datetime
    

class OrgOutput(OrgModel):
    id:Annotated[str,Field(alias="_id", description="Unique id of the organization")]  
    
    class Config:
        populate_by_name = True  # 👈 allows using 'id' instead of '_id'
    