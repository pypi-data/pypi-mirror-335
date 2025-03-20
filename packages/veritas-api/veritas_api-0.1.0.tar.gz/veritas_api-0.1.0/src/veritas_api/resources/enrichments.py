# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import enrichment_create_bulk_params
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
from ..types.enrichment_retrieve_response import EnrichmentRetrieveResponse
from ..types.enrichment_create_bulk_response import EnrichmentCreateBulkResponse

__all__ = ["EnrichmentsResource", "AsyncEnrichmentsResource"]


class EnrichmentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EnrichmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/VeritasLabsInc/veritas-api-python#accessing-raw-response-data-eg-headers
        """
        return EnrichmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EnrichmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/VeritasLabsInc/veritas-api-python#with_streaming_response
        """
        return EnrichmentsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnrichmentRetrieveResponse:
        """
        Get enrichment status and results

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v1/enrichments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnrichmentRetrieveResponse,
        )

    def create_bulk(
        self,
        *,
        candidates: Iterable[enrichment_create_bulk_params.Candidate],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnrichmentCreateBulkResponse:
        """
        Creates a bulk enrichment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/enrichments",
            body=maybe_transform({"candidates": candidates}, enrichment_create_bulk_params.EnrichmentCreateBulkParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnrichmentCreateBulkResponse,
        )


class AsyncEnrichmentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEnrichmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/VeritasLabsInc/veritas-api-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEnrichmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEnrichmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/VeritasLabsInc/veritas-api-python#with_streaming_response
        """
        return AsyncEnrichmentsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnrichmentRetrieveResponse:
        """
        Get enrichment status and results

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v1/enrichments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnrichmentRetrieveResponse,
        )

    async def create_bulk(
        self,
        *,
        candidates: Iterable[enrichment_create_bulk_params.Candidate],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnrichmentCreateBulkResponse:
        """
        Creates a bulk enrichment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/enrichments",
            body=await async_maybe_transform(
                {"candidates": candidates}, enrichment_create_bulk_params.EnrichmentCreateBulkParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnrichmentCreateBulkResponse,
        )


class EnrichmentsResourceWithRawResponse:
    def __init__(self, enrichments: EnrichmentsResource) -> None:
        self._enrichments = enrichments

        self.retrieve = to_raw_response_wrapper(
            enrichments.retrieve,
        )
        self.create_bulk = to_raw_response_wrapper(
            enrichments.create_bulk,
        )


class AsyncEnrichmentsResourceWithRawResponse:
    def __init__(self, enrichments: AsyncEnrichmentsResource) -> None:
        self._enrichments = enrichments

        self.retrieve = async_to_raw_response_wrapper(
            enrichments.retrieve,
        )
        self.create_bulk = async_to_raw_response_wrapper(
            enrichments.create_bulk,
        )


class EnrichmentsResourceWithStreamingResponse:
    def __init__(self, enrichments: EnrichmentsResource) -> None:
        self._enrichments = enrichments

        self.retrieve = to_streamed_response_wrapper(
            enrichments.retrieve,
        )
        self.create_bulk = to_streamed_response_wrapper(
            enrichments.create_bulk,
        )


class AsyncEnrichmentsResourceWithStreamingResponse:
    def __init__(self, enrichments: AsyncEnrichmentsResource) -> None:
        self._enrichments = enrichments

        self.retrieve = async_to_streamed_response_wrapper(
            enrichments.retrieve,
        )
        self.create_bulk = async_to_streamed_response_wrapper(
            enrichments.create_bulk,
        )
