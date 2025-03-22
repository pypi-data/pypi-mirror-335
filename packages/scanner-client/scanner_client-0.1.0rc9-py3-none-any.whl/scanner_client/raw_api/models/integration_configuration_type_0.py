from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.github_configuration import GithubConfiguration


T = TypeVar("T", bound="IntegrationConfigurationType0")


@_attrs_define
class IntegrationConfigurationType0:
    """
    Attributes:
        github (GithubConfiguration):
    """

    github: "GithubConfiguration"

    def to_dict(self) -> dict[str, Any]:
        github = self.github.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "Github": github,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.github_configuration import GithubConfiguration

        d = src_dict.copy()
        github = GithubConfiguration.from_dict(d.pop("Github"))

        integration_configuration_type_0 = cls(
            github=github,
        )

        return integration_configuration_type_0
