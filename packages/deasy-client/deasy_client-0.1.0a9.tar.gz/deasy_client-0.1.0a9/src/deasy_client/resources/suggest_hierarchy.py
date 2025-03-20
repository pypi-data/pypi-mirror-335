# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ..types import suggest_hierarchy_create_params
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
from ..types.condition_input_param import ConditionInputParam
from ..types.suggest_hierarchy_create_response import SuggestHierarchyCreateResponse

__all__ = ["SuggestHierarchyResource", "AsyncSuggestHierarchyResource"]


class SuggestHierarchyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SuggestHierarchyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-python#accessing-raw-response-data-eg-headers
        """
        return SuggestHierarchyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SuggestHierarchyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-python#with_streaming_response
        """
        return SuggestHierarchyResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        vdb_profile_name: str,
        condition: Optional[ConditionInputParam] | NotGiven = NOT_GIVEN,
        context_level: Optional[str] | NotGiven = NOT_GIVEN,
        current_tree: Optional[object] | NotGiven = NOT_GIVEN,
        dataslice_id: Optional[str] | NotGiven = NOT_GIVEN,
        file_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        llm_profile_name: Optional[str] | NotGiven = NOT_GIVEN,
        max_height: Optional[int] | NotGiven = NOT_GIVEN,
        node: Optional[object] | NotGiven = NOT_GIVEN,
        use_existing_tags: Optional[bool] | NotGiven = NOT_GIVEN,
        use_extracted_tags: Optional[bool] | NotGiven = NOT_GIVEN,
        user_context: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuggestHierarchyCreateResponse:
        """
        Suggest a hierarchical tag schema based on file content and existing metadata

        Attributes:

            vdb_profile_name: The name of the vector database profile to use for accessing file content.
            llm_profile_name: Optional name of the language model profile to use for generating suggestions. Defaults to DeasyLabs compute
            file_names: Optional list of specific files to analyze for the hierarchy suggestion.
            dataslice_id: Optional ID of a dataslice to pull files from for the hierarchy suggestion.
            current_tree: Optional existing hierarchy tree to build upon.
            node: Optional node location of the existing hierarchy tree to build upon.
            condition: Optional filtering condition to select specific files for analysis.
            user_context: Optional user-provided context to guide the suggestion process.
            context_level: Level at which to analyze content ('file' or 'chunk'). Defaults to 'file'.
            max_height: Maximum depth of the generated hierarchy tree. Defaults to 2.
            use_existing_tags: Whether to incorporate existing tags in suggestions. Defaults to False.
            use_extracted_tags: Whether to use previously extracted tags. Defaults to False.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/suggest_hierarchy",
            body=maybe_transform(
                {
                    "vdb_profile_name": vdb_profile_name,
                    "condition": condition,
                    "context_level": context_level,
                    "current_tree": current_tree,
                    "dataslice_id": dataslice_id,
                    "file_names": file_names,
                    "llm_profile_name": llm_profile_name,
                    "max_height": max_height,
                    "node": node,
                    "use_existing_tags": use_existing_tags,
                    "use_extracted_tags": use_extracted_tags,
                    "user_context": user_context,
                },
                suggest_hierarchy_create_params.SuggestHierarchyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuggestHierarchyCreateResponse,
        )


class AsyncSuggestHierarchyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSuggestHierarchyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSuggestHierarchyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSuggestHierarchyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-python#with_streaming_response
        """
        return AsyncSuggestHierarchyResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        vdb_profile_name: str,
        condition: Optional[ConditionInputParam] | NotGiven = NOT_GIVEN,
        context_level: Optional[str] | NotGiven = NOT_GIVEN,
        current_tree: Optional[object] | NotGiven = NOT_GIVEN,
        dataslice_id: Optional[str] | NotGiven = NOT_GIVEN,
        file_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        llm_profile_name: Optional[str] | NotGiven = NOT_GIVEN,
        max_height: Optional[int] | NotGiven = NOT_GIVEN,
        node: Optional[object] | NotGiven = NOT_GIVEN,
        use_existing_tags: Optional[bool] | NotGiven = NOT_GIVEN,
        use_extracted_tags: Optional[bool] | NotGiven = NOT_GIVEN,
        user_context: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuggestHierarchyCreateResponse:
        """
        Suggest a hierarchical tag schema based on file content and existing metadata

        Attributes:

            vdb_profile_name: The name of the vector database profile to use for accessing file content.
            llm_profile_name: Optional name of the language model profile to use for generating suggestions. Defaults to DeasyLabs compute
            file_names: Optional list of specific files to analyze for the hierarchy suggestion.
            dataslice_id: Optional ID of a dataslice to pull files from for the hierarchy suggestion.
            current_tree: Optional existing hierarchy tree to build upon.
            node: Optional node location of the existing hierarchy tree to build upon.
            condition: Optional filtering condition to select specific files for analysis.
            user_context: Optional user-provided context to guide the suggestion process.
            context_level: Level at which to analyze content ('file' or 'chunk'). Defaults to 'file'.
            max_height: Maximum depth of the generated hierarchy tree. Defaults to 2.
            use_existing_tags: Whether to incorporate existing tags in suggestions. Defaults to False.
            use_extracted_tags: Whether to use previously extracted tags. Defaults to False.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/suggest_hierarchy",
            body=await async_maybe_transform(
                {
                    "vdb_profile_name": vdb_profile_name,
                    "condition": condition,
                    "context_level": context_level,
                    "current_tree": current_tree,
                    "dataslice_id": dataslice_id,
                    "file_names": file_names,
                    "llm_profile_name": llm_profile_name,
                    "max_height": max_height,
                    "node": node,
                    "use_existing_tags": use_existing_tags,
                    "use_extracted_tags": use_extracted_tags,
                    "user_context": user_context,
                },
                suggest_hierarchy_create_params.SuggestHierarchyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuggestHierarchyCreateResponse,
        )


class SuggestHierarchyResourceWithRawResponse:
    def __init__(self, suggest_hierarchy: SuggestHierarchyResource) -> None:
        self._suggest_hierarchy = suggest_hierarchy

        self.create = to_raw_response_wrapper(
            suggest_hierarchy.create,
        )


class AsyncSuggestHierarchyResourceWithRawResponse:
    def __init__(self, suggest_hierarchy: AsyncSuggestHierarchyResource) -> None:
        self._suggest_hierarchy = suggest_hierarchy

        self.create = async_to_raw_response_wrapper(
            suggest_hierarchy.create,
        )


class SuggestHierarchyResourceWithStreamingResponse:
    def __init__(self, suggest_hierarchy: SuggestHierarchyResource) -> None:
        self._suggest_hierarchy = suggest_hierarchy

        self.create = to_streamed_response_wrapper(
            suggest_hierarchy.create,
        )


class AsyncSuggestHierarchyResourceWithStreamingResponse:
    def __init__(self, suggest_hierarchy: AsyncSuggestHierarchyResource) -> None:
        self._suggest_hierarchy = suggest_hierarchy

        self.create = async_to_streamed_response_wrapper(
            suggest_hierarchy.create,
        )
