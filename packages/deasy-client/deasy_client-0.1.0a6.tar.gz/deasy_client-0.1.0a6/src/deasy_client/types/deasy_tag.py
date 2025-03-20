# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DeasyTag"]


class DeasyTag(BaseModel):
    available_values: List[str]

    created_at: datetime

    description: str

    examples: List[Union[str, object]]

    name: str

    output_type: str

    tag_id: str

    updated_at: datetime

    username: str

    date_format: Optional[str] = None

    max_values: Optional[int] = FieldInfo(alias="maxValues", default=None)

    tuned: Optional[int] = None
