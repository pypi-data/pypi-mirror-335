from typing import List, Optional

from pydantic import BaseModel, Field

from .phrase_tms_api_models import UidReference


class UpdateCustomFieldDto(BaseModel):
    name: str = Field(min_length=0, max_length=255)
    allowedEntities: List[str]
    required: Optional[bool] = None
    description: Optional[str] = Field(min_length=0, max_length=500)
    addOptions: Optional[List[str]] = None
    removeOptions: Optional[List[UidReference]] = None