# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .deasy_tag import DeasyTag

__all__ = ["SuggestHierarchyCreateResponse", "CreatedTag"]


class CreatedTag(BaseModel):
    deasy_tag: DeasyTag

    new_available_values: List[str]


class SuggestHierarchyCreateResponse(BaseModel):
    suggestion: object

    created_tags: Optional[List[CreatedTag]] = None

    message: Optional[str] = None

    status_code: Optional[int] = None
