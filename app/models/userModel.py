from pydantic import BaseModel,Field,EmailStr
from typing import Annotated, Optional
from datetime import datetime, timezone # Important: import timezone



class User(BaseModel): # Inherit from beanie.Document
    username: Annotated[str, Field(
        ...,
        max_length=100,
        description="Unique username of user which will be used to login in application",
        examples=["user1"]
    )]
    firstname: Annotated[str, Field(
        ...,
        max_length=100,
        description="First name of the user",
        examples=["John"]
    )]
    lastname: Annotated[Optional[str], Field(
        None, # Changed from ... to None for Optional fields with default None
        max_length=100,
        description="Last name of the user",
        examples=["Doe"]
    )]
    email: Annotated[EmailStr, Field(
        ...,
        description="Email Id of the user",
        examples=["example@gmail.com"]
    )]
    # IMPORTANT: Do NOT store plain text password here.
    # This field will store the HASHED password.
    # The plain text password should be handled in an input model (e.g., for registration).
    hashed_password: Annotated[str, Field(
        ..., # Or you might make this Optional if it's set after creation
        description="Hashed password of the user",
        min_length=60, # Typical length for bcrypt/argon2 hashes, not min_length of plain text password
        max_length=100  # Adjust max_length based on your hashing algorithm output
    )]
    organizationId: Annotated[str, Field(
        ...,
        max_length=100,
        description="Id of the user's organization",
    )]
    isAdmin: Annotated[bool, Field( # Simplified to bool with default False
        default=False,
        description="User is admin or not",
        examples=[False]
    )]
    created_at: Annotated[datetime, Field(
        default_factory=datetime.datetime.now(timezone.utc),
        description="Timestamp of user creation (UTC)"
    )]
    updated_at: Annotated[datetime, Field(
        default_factory=datetime.datetime.now(timezone.utc),
        description="Timestamp of last user update (UTC)"
    )]

   

    # Optional: Lifecycle hook for updating 'updated_at'
    async def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)

    # Optional: Method to check password (after hashing)
    # This would typically be in a separate utility or service
    # def check_password(self, password: str) -> bool:
    #     # Use your hashing library (e.g., bcrypt) to check
    #     # return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
    #     pass    