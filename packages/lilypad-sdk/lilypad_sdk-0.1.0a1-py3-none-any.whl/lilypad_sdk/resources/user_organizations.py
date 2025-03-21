# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import UserRole, user_organization_create_params, user_organization_update_params
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
from ..types.user_role import UserRole
from ..types.user_organization import UserOrganization
from ..types.user_organization_list_response import UserOrganizationListResponse
from ..types.user_organization_delete_response import UserOrganizationDeleteResponse
from ..types.user_organization_get_users_response import UserOrganizationGetUsersResponse

__all__ = ["UserOrganizationsResource", "AsyncUserOrganizationsResource"]


class UserOrganizationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UserOrganizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Mirascope/lilypad-sdk-python#accessing-raw-response-data-eg-headers
        """
        return UserOrganizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UserOrganizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Mirascope/lilypad-sdk-python#with_streaming_response
        """
        return UserOrganizationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganization:
        """
        Create user organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/user-organizations",
            body=maybe_transform({"token": token}, user_organization_create_params.UserOrganizationCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganization,
        )

    def update(
        self,
        user_organization_uuid: str,
        *,
        role: UserRole,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganization:
        """
        Updates user organization

        Args:
          role: User role enum.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not user_organization_uuid:
            raise ValueError(
                f"Expected a non-empty value for `user_organization_uuid` but received {user_organization_uuid!r}"
            )
        return self._patch(
            f"/user-organizations/{user_organization_uuid}",
            body=maybe_transform({"role": role}, user_organization_update_params.UserOrganizationUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganization,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganizationListResponse:
        """Get all user organizations."""
        return self._get(
            "/user-organizations",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganizationListResponse,
        )

    def delete(
        self,
        user_organization_uuid: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganizationDeleteResponse:
        """
        Delete user organization by uuid

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not user_organization_uuid:
            raise ValueError(
                f"Expected a non-empty value for `user_organization_uuid` but received {user_organization_uuid!r}"
            )
        return self._delete(
            f"/user-organizations/{user_organization_uuid}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganizationDeleteResponse,
        )

    def get_users(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganizationGetUsersResponse:
        """Get all users of an organization."""
        return self._get(
            "/user-organizations/users",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganizationGetUsersResponse,
        )


class AsyncUserOrganizationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUserOrganizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Mirascope/lilypad-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUserOrganizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUserOrganizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Mirascope/lilypad-sdk-python#with_streaming_response
        """
        return AsyncUserOrganizationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganization:
        """
        Create user organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/user-organizations",
            body=await async_maybe_transform(
                {"token": token}, user_organization_create_params.UserOrganizationCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganization,
        )

    async def update(
        self,
        user_organization_uuid: str,
        *,
        role: UserRole,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganization:
        """
        Updates user organization

        Args:
          role: User role enum.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not user_organization_uuid:
            raise ValueError(
                f"Expected a non-empty value for `user_organization_uuid` but received {user_organization_uuid!r}"
            )
        return await self._patch(
            f"/user-organizations/{user_organization_uuid}",
            body=await async_maybe_transform(
                {"role": role}, user_organization_update_params.UserOrganizationUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganization,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganizationListResponse:
        """Get all user organizations."""
        return await self._get(
            "/user-organizations",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganizationListResponse,
        )

    async def delete(
        self,
        user_organization_uuid: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganizationDeleteResponse:
        """
        Delete user organization by uuid

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not user_organization_uuid:
            raise ValueError(
                f"Expected a non-empty value for `user_organization_uuid` but received {user_organization_uuid!r}"
            )
        return await self._delete(
            f"/user-organizations/{user_organization_uuid}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganizationDeleteResponse,
        )

    async def get_users(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserOrganizationGetUsersResponse:
        """Get all users of an organization."""
        return await self._get(
            "/user-organizations/users",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserOrganizationGetUsersResponse,
        )


class UserOrganizationsResourceWithRawResponse:
    def __init__(self, user_organizations: UserOrganizationsResource) -> None:
        self._user_organizations = user_organizations

        self.create = to_raw_response_wrapper(
            user_organizations.create,
        )
        self.update = to_raw_response_wrapper(
            user_organizations.update,
        )
        self.list = to_raw_response_wrapper(
            user_organizations.list,
        )
        self.delete = to_raw_response_wrapper(
            user_organizations.delete,
        )
        self.get_users = to_raw_response_wrapper(
            user_organizations.get_users,
        )


class AsyncUserOrganizationsResourceWithRawResponse:
    def __init__(self, user_organizations: AsyncUserOrganizationsResource) -> None:
        self._user_organizations = user_organizations

        self.create = async_to_raw_response_wrapper(
            user_organizations.create,
        )
        self.update = async_to_raw_response_wrapper(
            user_organizations.update,
        )
        self.list = async_to_raw_response_wrapper(
            user_organizations.list,
        )
        self.delete = async_to_raw_response_wrapper(
            user_organizations.delete,
        )
        self.get_users = async_to_raw_response_wrapper(
            user_organizations.get_users,
        )


class UserOrganizationsResourceWithStreamingResponse:
    def __init__(self, user_organizations: UserOrganizationsResource) -> None:
        self._user_organizations = user_organizations

        self.create = to_streamed_response_wrapper(
            user_organizations.create,
        )
        self.update = to_streamed_response_wrapper(
            user_organizations.update,
        )
        self.list = to_streamed_response_wrapper(
            user_organizations.list,
        )
        self.delete = to_streamed_response_wrapper(
            user_organizations.delete,
        )
        self.get_users = to_streamed_response_wrapper(
            user_organizations.get_users,
        )


class AsyncUserOrganizationsResourceWithStreamingResponse:
    def __init__(self, user_organizations: AsyncUserOrganizationsResource) -> None:
        self._user_organizations = user_organizations

        self.create = async_to_streamed_response_wrapper(
            user_organizations.create,
        )
        self.update = async_to_streamed_response_wrapper(
            user_organizations.update,
        )
        self.list = async_to_streamed_response_wrapper(
            user_organizations.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            user_organizations.delete,
        )
        self.get_users = async_to_streamed_response_wrapper(
            user_organizations.get_users,
        )
