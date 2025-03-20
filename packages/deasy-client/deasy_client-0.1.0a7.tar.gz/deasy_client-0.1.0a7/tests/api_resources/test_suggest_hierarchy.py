# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import Deasy, AsyncDeasy
from deasy_client.types import SuggestHierarchyCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSuggestHierarchy:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Deasy) -> None:
        suggest_hierarchy = client.suggest_hierarchy.create(
            vdb_profile_name="vdb_profile_name",
        )
        assert_matches_type(SuggestHierarchyCreateResponse, suggest_hierarchy, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Deasy) -> None:
        suggest_hierarchy = client.suggest_hierarchy.create(
            vdb_profile_name="vdb_profile_name",
            condition={
                "children": [],
                "condition": "AND",
                "tag": {
                    "name": "name",
                    "values": ["string"],
                },
            },
            context_level="context_level",
            current_tree={},
            dataslice_id="dataslice_id",
            file_names=["string"],
            llm_profile_name="llm_profile_name",
            max_height=0,
            node={},
            use_existing_tags=True,
            use_extracted_tags=True,
            user_context="user_context",
        )
        assert_matches_type(SuggestHierarchyCreateResponse, suggest_hierarchy, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Deasy) -> None:
        response = client.suggest_hierarchy.with_raw_response.create(
            vdb_profile_name="vdb_profile_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        suggest_hierarchy = response.parse()
        assert_matches_type(SuggestHierarchyCreateResponse, suggest_hierarchy, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Deasy) -> None:
        with client.suggest_hierarchy.with_streaming_response.create(
            vdb_profile_name="vdb_profile_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            suggest_hierarchy = response.parse()
            assert_matches_type(SuggestHierarchyCreateResponse, suggest_hierarchy, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSuggestHierarchy:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncDeasy) -> None:
        suggest_hierarchy = await async_client.suggest_hierarchy.create(
            vdb_profile_name="vdb_profile_name",
        )
        assert_matches_type(SuggestHierarchyCreateResponse, suggest_hierarchy, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeasy) -> None:
        suggest_hierarchy = await async_client.suggest_hierarchy.create(
            vdb_profile_name="vdb_profile_name",
            condition={
                "children": [],
                "condition": "AND",
                "tag": {
                    "name": "name",
                    "values": ["string"],
                },
            },
            context_level="context_level",
            current_tree={},
            dataslice_id="dataslice_id",
            file_names=["string"],
            llm_profile_name="llm_profile_name",
            max_height=0,
            node={},
            use_existing_tags=True,
            use_extracted_tags=True,
            user_context="user_context",
        )
        assert_matches_type(SuggestHierarchyCreateResponse, suggest_hierarchy, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeasy) -> None:
        response = await async_client.suggest_hierarchy.with_raw_response.create(
            vdb_profile_name="vdb_profile_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        suggest_hierarchy = await response.parse()
        assert_matches_type(SuggestHierarchyCreateResponse, suggest_hierarchy, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeasy) -> None:
        async with async_client.suggest_hierarchy.with_streaming_response.create(
            vdb_profile_name="vdb_profile_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            suggest_hierarchy = await response.parse()
            assert_matches_type(SuggestHierarchyCreateResponse, suggest_hierarchy, path=["response"])

        assert cast(Any, response.is_closed) is True
