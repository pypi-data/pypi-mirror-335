from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.slack_configuration import SlackConfiguration


T = TypeVar("T", bound="IntegrationConfigurationType1")


@_attrs_define
class IntegrationConfigurationType1:
    """
    Attributes:
        slack (SlackConfiguration):
    """

    slack: "SlackConfiguration"

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
        from ..models.slack_configuration import SlackConfiguration

        d = src_dict.copy()
        slack = SlackConfiguration.from_dict(d.pop("Slack"))

        integration_configuration_type_1 = cls(
            slack=slack,
        )

        return integration_configuration_type_1
