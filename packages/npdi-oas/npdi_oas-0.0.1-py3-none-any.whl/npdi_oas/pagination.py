from pydantic import BaseModel, Field
from typing import Any


class PaginatedResponse(BaseModel):
    results: list[Any] | None = None
    page: int | None = None
    total_pages: int | None = None
    total_results: int | None = None


