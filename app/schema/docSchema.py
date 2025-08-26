from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from datetime import datetime
from typing import Annotated, Optional, List, Dict, Any
from bson import ObjectId

# Fixed PyObjectId definition
PyObjectId = Annotated[str, BeforeValidator(str)]

class DocBase(BaseModel):
    name: Annotated[str, Field(..., max_length=200, description="Name of the file")]
    organizationId: Annotated[str, Field(..., description="Id of Organization")]

class DocOutput(DocBase):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id", description="Unique id of the Document")] 
    unique_filename: str
    path: str
    file_size: Optional[int] = Field(None, description="File size in bytes")
    uploadedAt: datetime
    status: str = Field(default="uploaded", description="Upload status")
    
    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class DocModel(BaseModel):
    name: str
    organizationId: str
    unique_filename: str
    path: str
    file_size: int
    uploadedAt: datetime
    status: str = "uploaded"
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# Processing result model for PDF processing
class ProcessingResult(BaseModel):
    status: str = Field(..., description="Processing status: success, failed, or partial")
    message: str = Field(..., description="Processing message")
    chunks_processed: int = Field(default=0, description="Number of chunks processed")
    documents_loaded: int = Field(default=0, description="Number of document pages loaded")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    error_details: Optional[str] = Field(None, description="Error details if processing failed")

# Upload response model
class DocumentUploadResponse(BaseModel):
    success: bool = Field(..., description="Whether the upload was successful")
    files_uploaded: int = Field(..., description="Number of files successfully uploaded")
    processing_result: ProcessingResult = Field(..., description="Result of PDF processing")
    document_ids: List[str] = Field(default_factory=list, description="List of uploaded document IDs")
    upload_time: Optional[float] = Field(None, description="Total upload time in seconds")
    errors: Optional[List[str]] = Field(default_factory=list, description="Any errors encountered")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# Bulk upload response for multiple organizations
class BulkUploadResponse(BaseModel):
    total_files: int
    successful_uploads: int
    failed_uploads: int
    upload_results: List[DocumentUploadResponse]
    summary: Dict[str, Any]
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# File validation model
class FileValidationResult(BaseModel):
    filename: str
    is_valid: bool
    file_size: int
    content_type: str
    errors: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# Search model (moved from other schema files for consistency)
class SearchBase(BaseModel):
    searchTxt: str = Field(..., min_length=1, description="Search query text")
    orgId: str = Field(..., min_length=1, description="Organization ID")
    documentId: str = Field(..., min_length=1, description="Document ID")
    limit: Optional[int] = Field(default=5, ge=1, le=20, description="Number of results")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        arbitrary_types_allowed=True
    )

# Document deletion request schema
class DocumentDeletionRequest(BaseModel):
    documentIds: List[str] = Field(..., min_items=1, description="List of document IDs to delete")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# Document deletion response schema
class DocumentDeletionErrors(BaseModel):
    invalid_ids: List[str] = Field(default_factory=list, description="Invalid document IDs")
    file_deletion_errors: List[str] = Field(default_factory=list, description="File deletion errors")
    vectorstore_deletion_errors: List[str] = Field(default_factory=list, description="Vectorstore deletion errors")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class DocumentDeletionResponse(BaseModel):
    success: bool = Field(..., description="Whether the deletion was successful")
    documents_requested: int = Field(..., description="Number of documents requested for deletion")
    documents_found: int = Field(..., description="Number of documents found in database")
    documents_deleted_from_mongodb: int = Field(..., description="Number of documents deleted from MongoDB")
    physical_files_deleted: int = Field(..., description="Number of physical files deleted")
    embeddings_deleted: int = Field(..., description="Number of embedding vectors deleted")
    deleted_document_ids: List[str] = Field(default_factory=list, description="IDs of deleted documents")
    deleted_file_paths: List[str] = Field(default_factory=list, description="Paths of deleted files")
    errors: DocumentDeletionErrors = Field(default_factory=DocumentDeletionErrors, description="Any errors encountered")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)