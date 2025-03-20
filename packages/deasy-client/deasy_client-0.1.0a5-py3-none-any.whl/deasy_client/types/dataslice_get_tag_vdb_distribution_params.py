# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["DatasliceGetTagVdbDistributionParams"]


class DatasliceGetTagVdbDistributionParams(TypedDict, total=False):
    dataslice_id: Optional[str]

    vector_db_config: Optional[object]
