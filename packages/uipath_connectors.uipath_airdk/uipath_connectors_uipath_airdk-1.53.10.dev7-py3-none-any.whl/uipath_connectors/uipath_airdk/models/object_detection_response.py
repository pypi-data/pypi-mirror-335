from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.object_detection_response_usage import ObjectDetectionResponseUsage
from ..models.object_detection_response_detected_objects_array_item_ref import (
    ObjectDetectionResponseDetectedObjectsArrayItemRef,
)
from ..models.object_detection_response_choices_array_item_ref import (
    ObjectDetectionResponseChoicesArrayItemRef,
)


class ObjectDetectionResponse(BaseModel):
    """
    Attributes:
        choices (Optional[list['ObjectDetectionResponseChoicesArrayItemRef']]):
        completion_tokens (Optional[int]): The count of tokens used to complete the object detection task. Example:
                84.0.
        created (Optional[int]): The date and time when the object detection task was created. Example: 1.724401299E9.
        detected_object_names (Optional[list[str]]):  Example: Package.
        detected_objects (Optional[list['ObjectDetectionResponseDetectedObjectsArrayItemRef']]):
        detected_objects_string (Optional[str]): Array of entities detected Example:
                [{"name":"Package","detected":"Yes","details":"Multiple packages are placed in front of the doorstep, clearly
                visible and accessible."},{"name":"Doorstep","detected":"No","details":"The doorstep is partially blocked by
                multiple packages."}].
        id (Optional[str]): A unique identifier for the detection request. Example:
                chatcmpl-9zJq77Je0RCy4tpS1BhLmwrlijjXl.
        model (Optional[str]): The AI model used for detecting objects. Example: gpt-4o-2024-05-13.
        object_ (Optional[str]): The specific object that the detection algorithm should look for. Example:
                chat.completion.
        prompt_tokens (Optional[int]): Specifies the count of tokens used in the prompt. Example: 874.0.
        text (Optional[str]): The textual description of the detected object. Example: {
                  "detected_entities": [
                    {
                      "name": "Package",
                      "detected": "Yes",
                      "details": "Multiple packages are placed in front of the doorstep, clearly visible and accessible."
                    },
                    {
                      "name": "Doorstep",
                      "detected": "No",
                      "details": "The doorstep is partially blocked by multiple packages."
                    }
                  ]
                }.
        total_tokens (Optional[int]): The total number of tokens consumed by the object detection task. Example: 958.0.
        usage (Optional[ObjectDetectionResponseUsage]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    choices: Optional[list["ObjectDetectionResponseChoicesArrayItemRef"]] = Field(
        alias="choices", default=None
    )
    completion_tokens: Optional[int] = Field(alias="completionTokens", default=None)
    created: Optional[int] = Field(alias="created", default=None)
    detected_object_names: Optional[list[str]] = Field(
        alias="detectedObjectNames", default=None
    )
    detected_objects: Optional[
        list["ObjectDetectionResponseDetectedObjectsArrayItemRef"]
    ] = Field(alias="detectedObjects", default=None)
    detected_objects_string: Optional[str] = Field(
        alias="detectedObjectsString", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    model: Optional[str] = Field(alias="model", default=None)
    object_: Optional[str] = Field(alias="object", default=None)
    prompt_tokens: Optional[int] = Field(alias="promptTokens", default=None)
    text: Optional[str] = Field(alias="text", default=None)
    total_tokens: Optional[int] = Field(alias="totalTokens", default=None)
    usage: Optional["ObjectDetectionResponseUsage"] = Field(alias="usage", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ObjectDetectionResponse"], src_dict: Dict[str, Any]):
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
