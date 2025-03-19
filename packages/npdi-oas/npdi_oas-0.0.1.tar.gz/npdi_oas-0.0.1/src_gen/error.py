from pydantic import BaseModel, Field
from typing import Any


class ErrorResponse(BaseModel):
    message: str = Field(..., description="A message describing the error.")


