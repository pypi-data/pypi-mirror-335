# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from deasy_client import DeasyLabs, AsyncDeasyLabs
from deasy_client.types import (
    GraphListResponse,
    GraphOperationResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGraph:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: DeasyLabs) -> None:
        graph = client.graph.create(
            graph_name="graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: DeasyLabs) -> None:
        graph = client.graph.create(
            graph_name="graph_name",
            graph_data={},
            graph_description="graph_description",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: DeasyLabs) -> None:
        response = client.graph.with_raw_response.create(
            graph_name="graph_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: DeasyLabs) -> None:
        with client.graph.with_streaming_response.create(
            graph_name="graph_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphOperationResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: DeasyLabs) -> None:
        graph = client.graph.update(
            graph_name="graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: DeasyLabs) -> None:
        graph = client.graph.update(
            graph_name="graph_name",
            graph_data={},
            graph_description="graph_description",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: DeasyLabs) -> None:
        response = client.graph.with_raw_response.update(
            graph_name="graph_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: DeasyLabs) -> None:
        with client.graph.with_streaming_response.update(
            graph_name="graph_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphOperationResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: DeasyLabs) -> None:
        graph = client.graph.list()
        assert_matches_type(GraphListResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: DeasyLabs) -> None:
        graph = client.graph.list(
            graph_names=["string"],
        )
        assert_matches_type(GraphListResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: DeasyLabs) -> None:
        response = client.graph.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphListResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: DeasyLabs) -> None:
        with client.graph.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphListResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: DeasyLabs) -> None:
        graph = client.graph.delete(
            graph_name="graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: DeasyLabs) -> None:
        response = client.graph.with_raw_response.delete(
            graph_name="graph_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: DeasyLabs) -> None:
        with client.graph.with_streaming_response.delete(
            graph_name="graph_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphOperationResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_upsert(self, client: DeasyLabs) -> None:
        graph = client.graph.upsert(
            graph_name="graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_upsert_with_all_params(self, client: DeasyLabs) -> None:
        graph = client.graph.upsert(
            graph_name="graph_name",
            graph_data={},
            graph_description="graph_description",
            new_graph_name="new_graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_upsert(self, client: DeasyLabs) -> None:
        response = client.graph.with_raw_response.upsert(
            graph_name="graph_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_upsert(self, client: DeasyLabs) -> None:
        with client.graph.with_streaming_response.upsert(
            graph_name="graph_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphOperationResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGraph:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.create(
            graph_name="graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.create(
            graph_name="graph_name",
            graph_data={},
            graph_description="graph_description",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDeasyLabs) -> None:
        response = await async_client.graph.with_raw_response.create(
            graph_name="graph_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDeasyLabs) -> None:
        async with async_client.graph.with_streaming_response.create(
            graph_name="graph_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphOperationResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.update(
            graph_name="graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.update(
            graph_name="graph_name",
            graph_data={},
            graph_description="graph_description",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDeasyLabs) -> None:
        response = await async_client.graph.with_raw_response.update(
            graph_name="graph_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDeasyLabs) -> None:
        async with async_client.graph.with_streaming_response.update(
            graph_name="graph_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphOperationResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.list()
        assert_matches_type(GraphListResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.list(
            graph_names=["string"],
        )
        assert_matches_type(GraphListResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDeasyLabs) -> None:
        response = await async_client.graph.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphListResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDeasyLabs) -> None:
        async with async_client.graph.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphListResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.delete(
            graph_name="graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDeasyLabs) -> None:
        response = await async_client.graph.with_raw_response.delete(
            graph_name="graph_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDeasyLabs) -> None:
        async with async_client.graph.with_streaming_response.delete(
            graph_name="graph_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphOperationResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_upsert(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.upsert(
            graph_name="graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_upsert_with_all_params(self, async_client: AsyncDeasyLabs) -> None:
        graph = await async_client.graph.upsert(
            graph_name="graph_name",
            graph_data={},
            graph_description="graph_description",
            new_graph_name="new_graph_name",
        )
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_upsert(self, async_client: AsyncDeasyLabs) -> None:
        response = await async_client.graph.with_raw_response.upsert(
            graph_name="graph_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphOperationResponse, graph, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_upsert(self, async_client: AsyncDeasyLabs) -> None:
        async with async_client.graph.with_streaming_response.upsert(
            graph_name="graph_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphOperationResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True
