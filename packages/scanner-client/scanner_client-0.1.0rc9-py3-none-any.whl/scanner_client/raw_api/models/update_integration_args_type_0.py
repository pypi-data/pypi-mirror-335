from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.update_slack_integration_args import UpdateSlackIntegrationArgs


T = TypeVar("T", bound="UpdateIntegrationArgsType0")


@_attrs_define
class UpdateIntegrationArgsType0:
    """
    Attributes:
        slack (UpdateSlackIntegrationArgs):
    """

    slack: "UpdateSlackIntegrationArgs"

    def to_dict(self) -> dict[str, Any]:
        slack = self.slack.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "Slack": slack,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.update_slack_integration_args import UpdateSlackIntegrationArgs

        d = src_dict.copy()
        slack = UpdateSlackIntegrationArgs.from_dict(d.pop("Slack"))

        update_integration_args_type_0 = cls(
            slack=slack,
        )

        return update_integration_args_type_0
