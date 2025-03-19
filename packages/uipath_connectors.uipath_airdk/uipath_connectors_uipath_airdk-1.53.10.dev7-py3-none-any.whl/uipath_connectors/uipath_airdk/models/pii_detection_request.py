from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.pii_detection_request_language import PIIDetectionRequestLanguage
from ..models.pii_detection_request_piiphi_category import (
    PIIDetectionRequestPIIPHICategory,
)


class PIIDetectionRequest(BaseModel):
    """
    Attributes:
        text (str): The document or text string containing the content to analyze for PII Example: Call our office at
                312-555-1234, or send an email to support@contoso.com.
        confidence_threshold (Optional[float]): The minimum confidence score required in order to be considered.  This
                is between 0-1 with 0 being the lowest and 1 being the highest confidence.  If not set, all detection results
                are returned regardless of the confidence score Example: 0.5.
        language_code (Optional[PIIDetectionRequestLanguage]): The language of the text or document input.  Defaults to
                English if not set.  Please note that not all PII/PHI categories are supported for all languages Example: en.
        pii_entity_categories (Optional[list[PIIDetectionRequestPIIPHICategory]]):  Example: PhoneNumber.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    text: str = Field(alias="text")
    confidence_threshold: Optional[float] = Field(
        alias="confidenceThreshold", default=None
    )
    language_code: Optional[PIIDetectionRequestLanguage] = Field(
        alias="languageCode", default=None
    )
    pii_entity_categories: Optional[list[PIIDetectionRequestPIIPHICategory]] = Field(
        alias="piiEntityCategories", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["PIIDetectionRequest"], src_dict: Dict[str, Any]):
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
