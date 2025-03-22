from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.create_webhook_integration_args import CreateWebhookIntegrationArgs


T = TypeVar("T", bound="CreateIntegrationArgsType1")


@_attrs_define
class CreateIntegrationArgsType1:
    """
    Attributes:
        webhook (CreateWebhookIntegrationArgs):
    """

    webhook: "CreateWebhookIntegrationArgs"

    def to_dict(self) -> dict[str, Any]:
        webhook = self.webhook.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "Webhook": webhook,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_webhook_integration_args import CreateWebhookIntegrationArgs

        d = src_dict.copy()
        webhook = CreateWebhookIntegrationArgs.from_dict(d.pop("Webhook"))

        create_integration_args_type_1 = cls(
            webhook=webhook,
        )

        return create_integration_args_type_1
