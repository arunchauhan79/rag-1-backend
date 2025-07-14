import os
from fastapi import  UploadFile
from schema import StandardResponse
from pymongo.asynchronous.database import AsyncDatabase
from core import BadRequestException
from datetime import datetime
from typing import List



async def upload_files(files: List[UploadFile], db: AsyncDatabase):
    try:
        UPLOAD_DIR = "uploaded_files"        
        
        
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        uploaded_files = []
        
        for file in files:
            # ✅ Validate file type
            if file.content_type != "application/pdf":
                raise BadRequestException(
                    f"Invalid file type for '{file.filename}'. Only PDFs allowed."
                )

            # ✅ Create unique filename
            filename = f"{datetime.now().isoformat()}_{file.filename}".replace(":", "-")
            file_path = os.path.join(UPLOAD_DIR, filename)

            # ✅ Save the file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            uploaded_files.append({
                "filename": file.filename,
                "saved_as": filename,
                "path": file_path
            })
    except Exception as e:
        raise BadRequestException(f"Error in uploading files, {e}")    
        
    return uploaded_files