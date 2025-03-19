from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class PIIDetectionResponseDetectedEntitiesArrayItemRef(BaseModel):
    """
    Attributes:
        confidence_score (Optional[float]): The Detected entities confidence score Example: 0.8.
        identifier (Optional[str]): Detected entities identifier Example: PhoneNumber-19.
        text (Optional[str]): Detected entities text Example: 312-555-1234.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    confidence_score: Optional[float] = Field(alias="confidenceScore", default=None)
    identifier: Optional[str] = Field(alias="identifier", default=None)
    text: Optional[str] = Field(alias="text", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["PIIDetectionResponseDetectedEntitiesArrayItemRef"],
        src_dict: Dict[str, Any],
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
