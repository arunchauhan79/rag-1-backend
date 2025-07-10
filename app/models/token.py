from pydantic import BaseModel, Field
from typing import Annotated

class Token(BaseModel):
    access_token:Annotated[str,Field(...,description="Access token for user authentication")]
    token_type: Annotated[str,Field(...,
                                    description="Type of token",
                                    default="bearer"
                                    )]