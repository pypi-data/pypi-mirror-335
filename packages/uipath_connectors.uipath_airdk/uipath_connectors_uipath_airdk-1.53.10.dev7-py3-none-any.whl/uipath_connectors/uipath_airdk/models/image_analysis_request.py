from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.image_analysis_request_image_type import ImageAnalysisRequestImageType


class ImageAnalysisRequest(BaseModel):
    """
    Attributes:
        image_type (ImageAnalysisRequestImageType): The type of image to send along with a message if image analysis is
                needed
        prompt (str): The user prompt for the chat completion request Example: Which organization holds the leading
                position in the field of Robotic Process Automation (RPA)?.
        frequency_penalty (Optional[int]): Number between -2.0 and 2.0. Positive values penalize new tokens based on
                their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
                Defaults to 0 Example: 1.0.
        image_url (Optional[str]): The publicly accessible URL of the image to send along with the user prompt
        instruction (Optional[str]): The system prompt or context instruction of the chat completion request Example:
                You are a informational provider.
        max_tokens (Optional[int]): The maximum number of tokens to generate in the completion. The token count of your
                prompt plus those from the result/completion cannot exceed the value provided for this field. It's best to set
                this value to be a less than the model maximum count so as to have some room for the prompt token count.
                Example: 50.0.
        n (Optional[int]): The number of completion choices to generate for the request. The higher the value of this
                field, the more the number of tokens that will get used, and hence will result in a higher cost, so the user
                needs to be aware of that when setting the value of this field. Defaults to 1 Example: 1.0.
        presence_penalty (Optional[int]): Number between -2.0 and 2.0. Positive values penalize new tokens based on
                whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Defaults to
                0 Example: 1.0.
        stop (Optional[str]): Up to 4 sequences where the API will stop generating further tokens. The returned text
                will not contain the stop sequence. Defaults to null.
        temperature (Optional[float]): The value of the creativity factor or sampling temperature to use. Higher values
                means the model will take more risks. Try 0.9 for more creative responses or completions, and 0 (also called
                argmax sampling) for ones with a well-defined or more exact answer.  The general recommendation is to alter,
                from the default value, this or the Nucleus Sample value, but not both values. Defaults to 1
        top_k (Optional[int]): A number between 1 and 40.  The higher the number the higher the diversity of generated
                text. Defaults to 40. Example: 40.0.
        topP (Optional[float]): A number between 0 and 1.  The lower the number, the lesser the randomness. Defaults to
                0.8. Example: 0.8.
        top_p (Optional[int]): A number between 0 and 1.  The lower the number, the fewer tokens are considered.
                Defaults to 1 Example: 1.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    image_type: ImageAnalysisRequestImageType = Field(alias="image_type")
    prompt: str = Field(alias="prompt")
    frequency_penalty: Optional[int] = Field(alias="frequency_penalty", default=None)
    image_url: Optional[str] = Field(alias="image_url", default=None)
    instruction: Optional[str] = Field(alias="instruction", default=None)
    max_tokens: Optional[int] = Field(alias="max_tokens", default=None)
    n: Optional[int] = Field(alias="n", default=None)
    presence_penalty: Optional[int] = Field(alias="presence_penalty", default=None)
    stop: Optional[str] = Field(alias="stop", default=None)
    temperature: Optional[float] = Field(alias="temperature", default=None)
    top_k: Optional[int] = Field(alias="topK", default=None)
    topP: Optional[float] = Field(alias="topP", default=None)
    top_p: Optional[int] = Field(alias="top_p", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ImageAnalysisRequest"], src_dict: Dict[str, Any]):
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
