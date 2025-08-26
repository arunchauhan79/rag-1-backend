
from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List,Annotated, Literal
from datetime import datetime
from bson import ObjectId


PyObjectId = Annotated[str, BeforeValidator(str)]


class QueryResponse(BaseModel):
    query: Optional[str] = None
    answer: str
    context: Optional[str] = None
    document_ids: Optional[List[str]] = Field(default_factory=list, description="MongoDB document IDs used")
    confidence: Optional[float] = None
    
    class Config:
        arbitrary_types_allowed = True

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

class QueryRequest(BaseModel):
    query: str
    org_id: str
    context_limit: Optional[int] = 5
    
    class Config:
        arbitrary_types_allowed = True       
        



class ChatHistoryCreate(BaseModel):
    sessionId: str
    userId: str
    orgId: str
    messages: List[ChatMessage]
    isActive:Annotated[Optional[Literal[True, False]],Field(default=True,description="Chat is still active or not",
                                 examples=["True"]
                                 )]

class ChatHistoryResponse(BaseModel):
    id: Annotated[PyObjectId, Field(alias="_id",
                                    description="Unique id of chat",
                                    examples=["64c21ffb7b1234567890abcd"])]
    sessionId: str
    userId: PyObjectId
    orgId: PyObjectId
    messages: List[ChatMessage]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
