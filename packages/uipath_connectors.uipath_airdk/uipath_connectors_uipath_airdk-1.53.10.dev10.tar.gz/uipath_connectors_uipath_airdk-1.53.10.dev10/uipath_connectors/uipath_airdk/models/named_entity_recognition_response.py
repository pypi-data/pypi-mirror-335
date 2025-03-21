from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.named_entity_recognition_response_entities_output_object_array_item_ref import (
    NamedEntityRecognitionResponseEntitiesOutputObjectArrayItemRef,
)


class NamedEntityRecognitionResponse(BaseModel):
    """
    Attributes:
        entities_output (Optional[str]): List of entities recognized by the NER model in the input text Example:
                [{"text":"Apple","type":"Organisation","start":0,"end":5}].
        entities_output_object (Optional[list['NamedEntityRecognitionResponseEntitiesOutputObjectArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    entities_output: Optional[str] = Field(alias="entitiesOutput", default=None)
    entities_output_object: Optional[
        list["NamedEntityRecognitionResponseEntitiesOutputObjectArrayItemRef"]
    ] = Field(alias="entitiesOutputObject", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["NamedEntityRecognitionResponse"], src_dict: Dict[str, Any]
    ):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
