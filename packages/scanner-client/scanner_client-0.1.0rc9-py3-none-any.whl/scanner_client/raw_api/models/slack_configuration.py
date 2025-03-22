from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SlackConfiguration")


@_attrs_define
class SlackConfiguration:
    """
    Attributes:
        channel_id (str):
        channel_name (str):
        channel (Union[Unset, str]):  Default: ''.
    """

    channel_id: str
    channel_name: str
    channel: Union[Unset, str] = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_id = self.channel_id

        channel_name = self.channel_name

        channel = self.channel

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "channel_id": channel_id,
                "channel_name": channel_name,
            }
        )
        if channel is not UNSET:
            field_dict["channel"] = channel

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        channel_id = d.pop("channel_id")

        channel_name = d.pop("channel_name")

        channel = d.pop("channel", UNSET)

        slack_configuration = cls(
            channel_id=channel_id,
            channel_name=channel_name,
            channel=channel,
        )

        slack_configuration.additional_properties = d
        return slack_configuration

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
