import uuid

from .http_err import get_body_and_handle_err
from .raw_api.api.event_sink import (
    list_event_sinks,
    create_event_sink,
    get_event_sink,
    update_event_sink,
    delete_event_sink,
)
from .raw_api.models import (
    ListEventSinksRequestData,
    CreateEventSinkRequestData,
    EventSink as EventSinkJson,
    UpdateEventSinkRequestData,
    CreateIntegrationArgsType0,
    CreateIntegrationArgsType1,
    CreateSlackIntegrationArgs,
    CreateWebhookIntegrationArgs,
    UpdateIntegrationArgsType0,
    UpdateIntegrationArgsType1,
    UpdateSlackIntegrationArgs,
    UpdateWebhookIntegrationArgs,
    DeleteEventSinkResponseData,
)
from .raw_api.client import AuthenticatedClient
from .raw_api.types import Unset, UNSET

CreateIntegrationArgs = CreateIntegrationArgsType0 | CreateIntegrationArgsType1
UpdateIntegrationArgs = UpdateIntegrationArgsType0 | UpdateIntegrationArgsType1


def create_slack_integration_args(
    slack_oauth_code: str,
    channel_id: str | Unset = UNSET,
    channel: str | Unset = UNSET,
) -> CreateIntegrationArgsType0:
    return CreateIntegrationArgsType0(
        slack=CreateSlackIntegrationArgs(
            slack_oauth_code=slack_oauth_code, channel_id=channel_id, channel=channel
        )
    )


def create_webhook_integration_args(url: str) -> CreateIntegrationArgsType1:
    return CreateIntegrationArgsType1(webhook=CreateWebhookIntegrationArgs(url=url))


def update_slack_integration_args(
    channel_id: str | Unset = UNSET,
    channel: str | Unset = UNSET,
) -> UpdateIntegrationArgsType0:
    return UpdateIntegrationArgsType0(
        slack=UpdateSlackIntegrationArgs(
            channel_id=channel_id, channel=channel
        )
    )


def update_webhook_integration_args(url: str) -> UpdateIntegrationArgsType1:
    return UpdateIntegrationArgsType1(webhook=UpdateWebhookIntegrationArgs(url=url))


class EventSink:
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list_all(self, tenant_id: str) -> list[EventSinkJson]:
        req_body = ListEventSinksRequestData(tenant_id=uuid.UUID(tenant_id))

        resp = list_event_sinks.sync_detailed(client=self._client, body=req_body)

        resp_body = get_body_and_handle_err(resp)

        return resp_body.data.event_sinks

    def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
        integration_args: CreateIntegrationArgs,
    ) -> EventSinkJson:
        req_body = CreateEventSinkRequestData(
            tenant_id=uuid.UUID(tenant_id),
            name=name,
            description=description,
            integration_args=integration_args,
        )

        resp = create_event_sink.sync_detailed(client=self._client, body=req_body)

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink

    def get(self, event_sink_id: str) -> EventSinkJson:
        resp = get_event_sink.sync_detailed(
            uuid.UUID(event_sink_id), client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink

    def update(
        self,
        event_sink_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
        integration_args: UpdateIntegrationArgs | Unset = UNSET,
    ) -> EventSinkJson:
        req_body = UpdateEventSinkRequestData(
            id=uuid.UUID(event_sink_id),
            name=name,
            description=description,
            integration_args=integration_args,
        )

        resp = update_event_sink.sync_detailed(
            uuid.UUID(event_sink_id), client=self._client, body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink

    def delete(self, event_sink_id: str) -> DeleteEventSinkResponseData:
        resp = delete_event_sink.sync_detailed(
            uuid.UUID(event_sink_id), client=self._client
        )

        return get_body_and_handle_err(resp)


class AsyncEventSink:
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list_all(self, tenant_id: str) -> list[EventSinkJson]:
        req_body = ListEventSinksRequestData(tenant_id=uuid.UUID(tenant_id))

        resp = await list_event_sinks.asyncio_detailed(
            client=self._client, body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.data.event_sinks

    async def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
        integration_args: CreateIntegrationArgs,
    ) -> EventSinkJson:
        req_body = CreateEventSinkRequestData(
            tenant_id=uuid.UUID(tenant_id),
            name=name,
            description=description,
            integration_args=integration_args,
        )

        resp = await create_event_sink.asyncio_detailed(
            client=self._client, body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink

    async def get(self, event_sink_id: str) -> EventSinkJson:
        resp = await get_event_sink.asyncio_detailed(
            uuid.UUID(event_sink_id), client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink

    async def update(
        self,
        event_sink_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
        integration_args: UpdateIntegrationArgs | Unset = UNSET,
    ) -> EventSinkJson:
        req_body = UpdateEventSinkRequestData(
            id=uuid.UUID(event_sink_id),
            name=name,
            description=description,
            integration_args=integration_args,
        )

        resp = await update_event_sink.asyncio_detailed(
            uuid.UUID(event_sink_id), client=self._client, body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.event_sink

    async def delete(self, event_sink_id: str) -> DeleteEventSinkResponseData:
        resp = await delete_event_sink.asyncio_detailed(
            uuid.UUID(event_sink_id), client=self._client
        )

        return get_body_and_handle_err(resp)
