from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Type

from ..types import File


class SignatureSimilarityBody(BaseModel):
    """
    Attributes:
        image_1 (File): First signature image to be compared (supported image files)
        image_2 (File): Second signature image to be compared (supported image files)
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    image_1: File = Field(alias="Image1")
    image_2: File = Field(alias="Image2")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SignatureSimilarityBody"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    def to_multipart(self) -> dict[str, Any]:
        image_1 = self.image_1.to_tuple()

        image_2 = self.image_2.to_tuple()

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_keys:
            field_dict[prop_name] = (
                None,
                str(self.__getitem__(prop)).encode(),
                "text/plain",
            )
        field_dict.update(
            {
                "Image1": image_1,
                "Image2": image_2,
            }
        )

        return field_dict

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
