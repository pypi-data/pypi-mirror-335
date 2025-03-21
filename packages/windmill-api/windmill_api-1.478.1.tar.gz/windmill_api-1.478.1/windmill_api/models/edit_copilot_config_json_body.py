from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.edit_copilot_config_json_body_ai_resource import EditCopilotConfigJsonBodyAiResource


T = TypeVar("T", bound="EditCopilotConfigJsonBody")


@_attrs_define
class EditCopilotConfigJsonBody:
    """
    Attributes:
        ai_models (List[str]):
        ai_resource (Union[Unset, EditCopilotConfigJsonBodyAiResource]):
        code_completion_model (Union[Unset, str]):
    """

    ai_models: List[str]
    ai_resource: Union[Unset, "EditCopilotConfigJsonBodyAiResource"] = UNSET
    code_completion_model: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ai_models = self.ai_models

        ai_resource: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ai_resource, Unset):
            ai_resource = self.ai_resource.to_dict()

        code_completion_model = self.code_completion_model

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ai_models": ai_models,
            }
        )
        if ai_resource is not UNSET:
            field_dict["ai_resource"] = ai_resource
        if code_completion_model is not UNSET:
            field_dict["code_completion_model"] = code_completion_model

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.edit_copilot_config_json_body_ai_resource import EditCopilotConfigJsonBodyAiResource

        d = src_dict.copy()
        ai_models = cast(List[str], d.pop("ai_models"))

        _ai_resource = d.pop("ai_resource", UNSET)
        ai_resource: Union[Unset, EditCopilotConfigJsonBodyAiResource]
        if isinstance(_ai_resource, Unset):
            ai_resource = UNSET
        else:
            ai_resource = EditCopilotConfigJsonBodyAiResource.from_dict(_ai_resource)

        code_completion_model = d.pop("code_completion_model", UNSET)

        edit_copilot_config_json_body = cls(
            ai_models=ai_models,
            ai_resource=ai_resource,
            code_completion_model=code_completion_model,
        )

        edit_copilot_config_json_body.additional_properties = d
        return edit_copilot_config_json_body

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
