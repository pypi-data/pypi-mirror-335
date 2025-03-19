from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class ContentGenerationResponseDetectedEntitiesArrayItemRef(BaseModel):
    """
    Attributes:
        category (Optional[str]): It represents the detected category of the text. Example: Person.
        confidence_score (Optional[int]): A numerical value representing the AI's certainty in the entity detection
                Example: 1.0.
        identifier (Optional[str]): Unique code representing a detected entity in the text. Example: Person-336.
        text (Optional[str]): The text of the entity that was detected in the input. Example: John Smith.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Optional[str] = Field(alias="category", default=None)
    confidence_score: Optional[int] = Field(alias="confidenceScore", default=None)
    identifier: Optional[str] = Field(alias="identifier", default=None)
    text: Optional[str] = Field(alias="text", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["ContentGenerationResponseDetectedEntitiesArrayItemRef"],
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
