from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.image_analysis_response_usage import ImageAnalysisResponseUsage
from ..models.image_analysis_response_choices_array_item_ref import (
    ImageAnalysisResponseChoicesArrayItemRef,
)


class ImageAnalysisResponse(BaseModel):
    """
    Attributes:
        choices (Optional[list['ImageAnalysisResponseChoicesArrayItemRef']]):
        completion_tokens (Optional[int]): The number of tokens the model is allowed to use for generating the
                completion Example: 259.0.
        created (Optional[int]): The Created Example: 1.709197578E9.
        id (Optional[str]): The ID Example: chatcmpl-8xWeoCeGSDzgCUaMs3edg3X6n78PP.
        model (Optional[str]): The name or ID of the model or deployment to use for the chat completion Example:
                gpt-35-turbo-16k.
        object_ (Optional[str]): The Object Example: chat.completion.
        prompt_tokens (Optional[int]): The number of tokens used in the prompt for generating the completion Example:
                653.0.
        text (Optional[str]): The image analysis completion text Example: UiPath is widely considered to be the leading
                organization in the field of Robotic Process Automation (RPA). It offers a comprehensive RPA platform that
                enables businesses to automate repetitive tasks, streamline processes, and improve operational efficiency.
                UiPath has gained significant.
        total_tokens (Optional[int]): The count of total tokens processed in the request Example: 912.0.
        usage (Optional[ImageAnalysisResponseUsage]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    choices: Optional[list["ImageAnalysisResponseChoicesArrayItemRef"]] = Field(
        alias="choices", default=None
    )
    completion_tokens: Optional[int] = Field(alias="completionTokens", default=None)
    created: Optional[int] = Field(alias="created", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    model: Optional[str] = Field(alias="model", default=None)
    object_: Optional[str] = Field(alias="object", default=None)
    prompt_tokens: Optional[int] = Field(alias="promptTokens", default=None)
    text: Optional[str] = Field(alias="text", default=None)
    total_tokens: Optional[int] = Field(alias="totalTokens", default=None)
    usage: Optional["ImageAnalysisResponseUsage"] = Field(alias="usage", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ImageAnalysisResponse"], src_dict: Dict[str, Any]):
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
