# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ..types import (
    graph_list_params,
    graph_create_params,
    graph_delete_params,
    graph_update_params,
    graph_upsert_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.graph_list_response import GraphListResponse
from ..types.graph_operation_response import GraphOperationResponse

__all__ = ["GraphResource", "AsyncGraphResource"]


class GraphResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GraphResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-python#accessing-raw-response-data-eg-headers
        """
        return GraphResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GraphResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-python#with_streaming_response
        """
        return GraphResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        graph_name: str,
        graph_data: Optional[object] | NotGiven = NOT_GIVEN,
        graph_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphOperationResponse:
        """
        Create a new graph.

        Attributes:

            graph_name: The name of the graph to create.
            graph_description: The description of the graph to create.
            graph_data: The data of the graph to create.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/graph/create",
            body=maybe_transform(
                {
                    "graph_name": graph_name,
                    "graph_data": graph_data,
                    "graph_description": graph_description,
                },
                graph_create_params.GraphCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphOperationResponse,
        )

    def update(
        self,
        *,
        graph_name: str,
        graph_data: Optional[object] | NotGiven = NOT_GIVEN,
        graph_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphOperationResponse:
        """
        Update a graph in the database.

        Attributes:

            graph_name: The name of the graph to update.
            graph_description: The description of the graph to update.
            graph_data: The data of the graph to update.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/graph/update",
            body=maybe_transform(
                {
                    "graph_name": graph_name,
                    "graph_data": graph_data,
                    "graph_description": graph_description,
                },
                graph_update_params.GraphUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphOperationResponse,
        )

    def list(
        self,
        *,
        graph_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphListResponse:
        """
        List all graphs for the authenticated user.

        Attributes:

            graph_names: The names of the graphs to retrieve.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/graph/list",
            body=maybe_transform({"graph_names": graph_names}, graph_list_params.GraphListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphListResponse,
        )

    def delete(
        self,
        *,
        graph_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphOperationResponse:
        """
        Delete a graph by name.

        Attributes:

            graph_name: The name of the graph to delete.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/graph/delete",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"graph_name": graph_name}, graph_delete_params.GraphDeleteParams),
            ),
            cast_to=GraphOperationResponse,
        )

    def upsert(
        self,
        *,
        graph_name: str,
        graph_data: Optional[object] | NotGiven = NOT_GIVEN,
        graph_description: Optional[str] | NotGiven = NOT_GIVEN,
        new_graph_name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphOperationResponse:
        """
        Upsert a graph in the database.

        Attributes:

            graph_name: The stored name of the graph to upsert.
            new_graph_name: The new name of the graph to upsert.
            graph_description: The description of the graph to upsert.
            graph_data: The data of the graph to upsert.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/graph/upsert",
            body=maybe_transform(
                {
                    "graph_name": graph_name,
                    "graph_data": graph_data,
                    "graph_description": graph_description,
                    "new_graph_name": new_graph_name,
                },
                graph_upsert_params.GraphUpsertParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphOperationResponse,
        )


class AsyncGraphResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGraphResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGraphResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGraphResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-python#with_streaming_response
        """
        return AsyncGraphResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        graph_name: str,
        graph_data: Optional[object] | NotGiven = NOT_GIVEN,
        graph_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphOperationResponse:
        """
        Create a new graph.

        Attributes:

            graph_name: The name of the graph to create.
            graph_description: The description of the graph to create.
            graph_data: The data of the graph to create.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/graph/create",
            body=await async_maybe_transform(
                {
                    "graph_name": graph_name,
                    "graph_data": graph_data,
                    "graph_description": graph_description,
                },
                graph_create_params.GraphCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphOperationResponse,
        )

    async def update(
        self,
        *,
        graph_name: str,
        graph_data: Optional[object] | NotGiven = NOT_GIVEN,
        graph_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphOperationResponse:
        """
        Update a graph in the database.

        Attributes:

            graph_name: The name of the graph to update.
            graph_description: The description of the graph to update.
            graph_data: The data of the graph to update.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/graph/update",
            body=await async_maybe_transform(
                {
                    "graph_name": graph_name,
                    "graph_data": graph_data,
                    "graph_description": graph_description,
                },
                graph_update_params.GraphUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphOperationResponse,
        )

    async def list(
        self,
        *,
        graph_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphListResponse:
        """
        List all graphs for the authenticated user.

        Attributes:

            graph_names: The names of the graphs to retrieve.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/graph/list",
            body=await async_maybe_transform({"graph_names": graph_names}, graph_list_params.GraphListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphListResponse,
        )

    async def delete(
        self,
        *,
        graph_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphOperationResponse:
        """
        Delete a graph by name.

        Attributes:

            graph_name: The name of the graph to delete.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/graph/delete",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"graph_name": graph_name}, graph_delete_params.GraphDeleteParams),
            ),
            cast_to=GraphOperationResponse,
        )

    async def upsert(
        self,
        *,
        graph_name: str,
        graph_data: Optional[object] | NotGiven = NOT_GIVEN,
        graph_description: Optional[str] | NotGiven = NOT_GIVEN,
        new_graph_name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphOperationResponse:
        """
        Upsert a graph in the database.

        Attributes:

            graph_name: The stored name of the graph to upsert.
            new_graph_name: The new name of the graph to upsert.
            graph_description: The description of the graph to upsert.
            graph_data: The data of the graph to upsert.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/graph/upsert",
            body=await async_maybe_transform(
                {
                    "graph_name": graph_name,
                    "graph_data": graph_data,
                    "graph_description": graph_description,
                    "new_graph_name": new_graph_name,
                },
                graph_upsert_params.GraphUpsertParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphOperationResponse,
        )


class GraphResourceWithRawResponse:
    def __init__(self, graph: GraphResource) -> None:
        self._graph = graph

        self.create = to_raw_response_wrapper(
            graph.create,
        )
        self.update = to_raw_response_wrapper(
            graph.update,
        )
        self.list = to_raw_response_wrapper(
            graph.list,
        )
        self.delete = to_raw_response_wrapper(
            graph.delete,
        )
        self.upsert = to_raw_response_wrapper(
            graph.upsert,
        )


class AsyncGraphResourceWithRawResponse:
    def __init__(self, graph: AsyncGraphResource) -> None:
        self._graph = graph

        self.create = async_to_raw_response_wrapper(
            graph.create,
        )
        self.update = async_to_raw_response_wrapper(
            graph.update,
        )
        self.list = async_to_raw_response_wrapper(
            graph.list,
        )
        self.delete = async_to_raw_response_wrapper(
            graph.delete,
        )
        self.upsert = async_to_raw_response_wrapper(
            graph.upsert,
        )


class GraphResourceWithStreamingResponse:
    def __init__(self, graph: GraphResource) -> None:
        self._graph = graph

        self.create = to_streamed_response_wrapper(
            graph.create,
        )
        self.update = to_streamed_response_wrapper(
            graph.update,
        )
        self.list = to_streamed_response_wrapper(
            graph.list,
        )
        self.delete = to_streamed_response_wrapper(
            graph.delete,
        )
        self.upsert = to_streamed_response_wrapper(
            graph.upsert,
        )


class AsyncGraphResourceWithStreamingResponse:
    def __init__(self, graph: AsyncGraphResource) -> None:
        self._graph = graph

        self.create = async_to_streamed_response_wrapper(
            graph.create,
        )
        self.update = async_to_streamed_response_wrapper(
            graph.update,
        )
        self.list = async_to_streamed_response_wrapper(
            graph.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            graph.delete,
        )
        self.upsert = async_to_streamed_response_wrapper(
            graph.upsert,
        )
