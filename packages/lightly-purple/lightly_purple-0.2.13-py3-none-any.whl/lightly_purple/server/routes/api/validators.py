"""General purple API models."""

from pydantic import BaseModel
from sqlmodel import Field


class Paginated(BaseModel):
    """Paginated query parameters."""

    offset: int = Field(0, ge=0, description="Offset for pagination")
    limit: int = Field(100, gt=0, le=100, description="Limit for pagination")
