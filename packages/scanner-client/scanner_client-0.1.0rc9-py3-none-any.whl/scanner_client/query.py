import uuid

from .http_err import get_body_and_handle_err
from .raw_api.api.query import query_progress, start_blocking_query, start_query
from .raw_api.client import AuthenticatedClient
from .raw_api.models import (
    AdHocQueryProgressResponse,
    LogEventId,
    StartAdHocQueryRequestData,
    StartAdHocQueryResponse,
)
from .raw_api.types import Unset, UNSET


class Query:
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def start_query(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> StartAdHocQueryResponse:
        req_data = StartAdHocQueryRequestData(
            query=query_text,
            start_time=start_time,
            end_time=end_time,
            start_leid=start_leid,
            end_leid=end_leid,
            scan_back_to_front=scan_back_to_front,
            max_rows=max_rows,
            max_bytes=max_bytes,
        )

        resp = start_query.sync_detailed(client=self._client, body=req_data)

        return get_body_and_handle_err(resp)

    def query_progress(self, qr_id: str) -> AdHocQueryProgressResponse:
        resp = query_progress.sync_detailed(uuid.UUID(qr_id), client=self._client)

        return get_body_and_handle_err(resp)

    def blocking_query(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> AdHocQueryProgressResponse:
        req_data = StartAdHocQueryRequestData(
            query=query_text,
            start_time=start_time,
            end_time=end_time,
            start_leid=start_leid,
            end_leid=end_leid,
            scan_back_to_front=scan_back_to_front,
            max_rows=max_rows,
            max_bytes=max_bytes,
        )

        resp = start_blocking_query.sync_detailed(client=self._client, body=req_data)

        return get_body_and_handle_err(resp)


class AsyncQuery:
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def start_query(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> StartAdHocQueryResponse:
        req_data = StartAdHocQueryRequestData(
            query=query_text,
            start_time=start_time,
            end_time=end_time,
            start_leid=start_leid,
            end_leid=end_leid,
            scan_back_to_front=scan_back_to_front,
            max_rows=max_rows,
            max_bytes=max_bytes,
        )

        resp = await start_query.asyncio_detailed(client=self._client, body=req_data)

        return get_body_and_handle_err(resp)

    async def query_progress(self, qr_id: str) -> AdHocQueryProgressResponse:
        resp = await query_progress.asyncio_detailed(
            uuid.UUID(qr_id), client=self._client
        )

        return get_body_and_handle_err(resp)

    async def blocking_query(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> AdHocQueryProgressResponse:
        req_data = StartAdHocQueryRequestData(
            query=query_text,
            start_time=start_time,
            end_time=end_time,
            start_leid=start_leid,
            end_leid=end_leid,
            scan_back_to_front=scan_back_to_front,
            max_rows=max_rows,
            max_bytes=max_bytes,
        )

        resp = await start_blocking_query.asyncio_detailed(
            client=self._client, body=req_data
        )

        return get_body_and_handle_err(resp)
