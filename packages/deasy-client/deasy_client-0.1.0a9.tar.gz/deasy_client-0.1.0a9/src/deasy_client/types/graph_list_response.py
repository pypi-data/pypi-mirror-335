# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from .._models import BaseModel

__all__ = ["GraphListResponse", "Graph"]


class Graph(BaseModel):
    created_at: datetime

    graph_data: object

    graph_description: str

    graph_id: str

    graph_name: str

    updated_at: datetime

    user_id: str


class GraphListResponse(BaseModel):
    graphs: List[Graph]
