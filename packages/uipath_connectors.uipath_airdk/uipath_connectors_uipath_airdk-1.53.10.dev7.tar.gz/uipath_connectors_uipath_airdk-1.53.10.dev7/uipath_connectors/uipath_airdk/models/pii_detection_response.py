from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.pii_detection_response_detected_entities_array_item_ref import (
    PIIDetectionResponseDetectedEntitiesArrayItemRef,
)


class PIIDetectionResponse(BaseModel):
    """
    Attributes:
        detected_entities (Optional[list['PIIDetectionResponseDetectedEntitiesArrayItemRef']]):
        initial_text (Optional[str]): The Initial text Example: Call our office at 312-555-1234, or send an email to
                support@contoso.com.
        masked_text (Optional[str]): Redacted text for all PII/PHI discovered in input Example: Call our office at
                PhoneNumber-19, or send an email to Email-53.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    detected_entities: Optional[
        list["PIIDetectionResponseDetectedEntitiesArrayItemRef"]
    ] = Field(alias="detectedEntities", default=None)
    initial_text: Optional[str] = Field(alias="initialText", default=None)
    masked_text: Optional[str] = Field(alias="maskedText", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["PIIDetectionResponse"], src_dict: Dict[str, Any]):
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
