from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.create_integration_args_type_0 import CreateIntegrationArgsType0
    from ..models.create_integration_args_type_1 import CreateIntegrationArgsType1


T = TypeVar("T", bound="CreateEventSinkRequestData")


@_attrs_define
class CreateEventSinkRequestData:
    """
    Attributes:
        description (str):
        integration_args (Union['CreateIntegrationArgsType0', 'CreateIntegrationArgsType1']):
        name (str):
        tenant_id (UUID):
    """

    description: str
    integration_args: Union["CreateIntegrationArgsType0", "CreateIntegrationArgsType1"]
    name: str
    tenant_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.create_integration_args_type_0 import CreateIntegrationArgsType0

        description = self.description

        integration_args: dict[str, Any]
        if isinstance(self.integration_args, CreateIntegrationArgsType0):
            integration_args = self.integration_args.to_dict()
        else:
            integration_args = self.integration_args.to_dict()

        name = self.name

        tenant_id = str(self.tenant_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "integration_args": integration_args,
                "name": name,
                "tenant_id": tenant_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_integration_args_type_0 import CreateIntegrationArgsType0
        from ..models.create_integration_args_type_1 import CreateIntegrationArgsType1

        d = src_dict.copy()
        description = d.pop("description")

        def _parse_integration_args(data: object) -> Union["CreateIntegrationArgsType0", "CreateIntegrationArgsType1"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_integration_args_type_0 = CreateIntegrationArgsType0.from_dict(data)

                return componentsschemas_create_integration_args_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_create_integration_args_type_1 = CreateIntegrationArgsType1.from_dict(data)

            return componentsschemas_create_integration_args_type_1

        integration_args = _parse_integration_args(d.pop("integration_args"))

        name = d.pop("name")

        tenant_id = UUID(d.pop("tenant_id"))

        create_event_sink_request_data = cls(
            description=description,
            integration_args=integration_args,
            name=name,
            tenant_id=tenant_id,
        )

        create_event_sink_request_data.additional_properties = d
        return create_event_sink_request_data

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
