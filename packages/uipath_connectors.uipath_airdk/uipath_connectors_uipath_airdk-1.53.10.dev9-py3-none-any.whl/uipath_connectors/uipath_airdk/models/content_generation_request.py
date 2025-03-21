from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.content_generation_request_context_grounding import (
    ContentGenerationRequestContextGrounding,
)
from ..models.content_generation_request_language_code import (
    ContentGenerationRequestLanguageCode,
)
from ..models.content_generation_request_pii_entity_categories import (
    ContentGenerationRequestPiiEntityCategories,
)


class ContentGenerationRequest(BaseModel):
    """
    Attributes:
        prompt (str): The user prompt for the chat completion request Example: Which organization holds the leading
                position in the field of Robotic Process Automation (RPA)?.
        confidence_threshold (Optional[float]): The minimum confidence score required in order to qualify as PII and be
                redacted Default: 0.75. Example: 0.5.
        context_grounding (Optional[ContentGenerationRequestContextGrounding]): Ground the prompt in context to increase
                quality and accuracy of the output.  This feature allows users to insert proprietary business logic and
                knowledge into the prompt.  If selected, users can reference an Orchestrator Bucket where documents have been
                uploaded or upload a file directly for one time use. Default: ContentGenerationRequestContextGrounding.NONE.
        frequency_penalty (Optional[int]): Number between -2.0 and 2.0. Positive values penalize new tokens based on
                their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
                Defaults to 0 Default: 0. Example: 1.0.
        index_id (Optional[str]): Name or ID of the index to ground the prompt in Example: None.
        instruction (Optional[str]): The system prompt or context instruction of the chat completion request Default:
                'You are a helpful assistant'. Example: You are a informational provider.
        is_filter_pii_enabled (Optional[bool]): If set to true, any detected PII/PHI will be masked before sending to
                the LLM. If false, detected PII will be included in the prompt.  In both cases, the detected PII will be
                available in the output.  Note that if set to true the quality of the output may be impacted. Default: False.
        is_pii_enabled (Optional[bool]): Whether to detect PII from the input prompt.  Defaults to false. Default:
                False.
        language_code (Optional[ContentGenerationRequestLanguageCode]): The language of the prompt input and output to
                scan for PII.
        max_tokens (Optional[int]): The maximum number of tokens to generate in the completion.  The token count of your
                prompt plus those from the result/completion cannot exceed the value provided for this field. It's best to set
                this value to be a less than the model maximum count so as to have some room for the prompt token count.
                Example: 50.0.
        n (Optional[int]): The number of completion choices to generate for the request. The higher the value of this
                field, the more the number of tokens that will get used, and hence will result in a higher cost, so the user
                needs to be aware of that when setting the value of this field. Defaults to 1 Default: 1. Example: 1.0.
        number_of_results (Optional[int]): Indicates the number of results to be returned. Default: 3. Example: 1.0.
        pii_entity_categories (Optional[list['ContentGenerationRequestPiiEntityCategories']]):
        presence_penalty (Optional[int]): Number between -2.0 and 2.0. Positive values penalize new tokens based on
                whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Defaults to
                0 Default: 0. Example: 1.0.
        stop (Optional[str]): Up to 4 sequences where the API will stop generating further tokens. The returned text
                will not contain the stop sequence. Defaults to null.
        temperature (Optional[float]): The value of the creativity factor or sampling temperature to use. Higher values
                means the model will take more risks. Try 0.9 for more creative responses or completions, and 0 (also called
                argmax sampling) for ones with a well-defined or more exact answer.  The general recommendation is to alter,
                from the default value, this or the Nucleus Sample value, but not both values. Defaults to 1 Default: 0.0.
        top_k (Optional[int]): A number between 1 and 40.  The higher the number the higher the diversity of generated
                text. Defaults to 40. Default: 40. Example: 40.0.
        top_p (Optional[float]): A number between 0 and 1.  The lower the number, the lesser the randomness. Defaults to
                0.8. Default: 0.8. Example: 0.8.
        top_p (Optional[int]): A number between 0 and 1.  The lower the number, the fewer tokens are considered.
                Defaults to 1 Default: 1. Example: 1.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    prompt: str = Field(alias="prompt")
    confidence_threshold: Optional[float] = Field(
        alias="confidenceThreshold", default=0.75
    )
    context_grounding: Optional["ContentGenerationRequestContextGrounding"] = Field(
        alias="contextGrounding", default=ContentGenerationRequestContextGrounding.NONE
    )
    frequency_penalty: Optional[int] = Field(alias="frequency_penalty", default=0)
    index_id: Optional[str] = Field(alias="indexID", default=None)
    instruction: Optional[str] = Field(
        alias="instruction", default="You are a helpful assistant"
    )
    is_filter_pii_enabled: Optional[bool] = Field(
        alias="isFilterPIIEnabled", default=False
    )
    is_pii_enabled: Optional[bool] = Field(alias="isPIIEnabled", default=False)
    language_code: Optional["ContentGenerationRequestLanguageCode"] = Field(
        alias="languageCode", default=None
    )
    max_tokens: Optional[int] = Field(alias="max_tokens", default=None)
    n: Optional[int] = Field(alias="n", default=1)
    number_of_results: Optional[int] = Field(alias="numberOfResults", default=3)
    pii_entity_categories: Optional[
        list["ContentGenerationRequestPiiEntityCategories"]
    ] = Field(alias="piiEntityCategories", default=None)
    presence_penalty: Optional[int] = Field(alias="presence_penalty", default=0)
    stop: Optional[str] = Field(alias="stop", default=None)
    temperature: Optional[float] = Field(alias="temperature", default=0.0)
    top_k: Optional[int] = Field(alias="topK", default=40)
    top_p: Optional[float] = Field(alias="topP", default=0.8)
    top_p: Optional[int] = Field(alias="top_p", default=1)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ContentGenerationRequest"], src_dict: Dict[str, Any]):
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
