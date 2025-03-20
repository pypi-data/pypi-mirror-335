# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["DatasliceCreateParams"]


class DatasliceCreateParams(TypedDict, total=False):
    dataslice_name: Required[str]

    graph_id: Required[str]

    latest_graph: Required[object]

    vdb_profile_name: Required[str]

    condition: Optional["ConditionInputParam"]

    data_points: Optional[int]

    description: Optional[str]

    status: str


from .condition_input_param import ConditionInputParam
