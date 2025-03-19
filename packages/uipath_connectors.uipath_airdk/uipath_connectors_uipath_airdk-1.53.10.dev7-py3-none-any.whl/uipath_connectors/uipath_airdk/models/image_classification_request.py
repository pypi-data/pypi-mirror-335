from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.image_classification_request_image_type import (
    ImageClassificationRequestImageType,
)
from ..models.image_classification_request_categories import (
    ImageClassificationRequestCategories,
)


class ImageClassificationRequest(BaseModel):
    """
    Attributes:
        categories (ImageClassificationRequestCategories): Categories
        image_type (ImageClassificationRequestImageType): The type of image to send along with a message if image
                analysis is needed
        description (Optional[str]): Description of the given image
        image_url (Optional[str]): The publicly accessible URL of the image to send along with the user prompt
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    categories: "ImageClassificationRequestCategories" = Field(alias="categories")
    image_type: ImageClassificationRequestImageType = Field(alias="image_type")
    description: Optional[str] = Field(alias="description", default=None)
    image_url: Optional[str] = Field(alias="image_url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ImageClassificationRequest"], src_dict: Dict[str, Any]):
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
