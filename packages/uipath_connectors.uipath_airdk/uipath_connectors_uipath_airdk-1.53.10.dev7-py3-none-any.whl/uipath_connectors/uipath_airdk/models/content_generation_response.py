from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.content_generation_response_choices_array_item_ref import (
    ContentGenerationResponseChoicesArrayItemRef,
)
from ..models.content_generation_response_usage import ContentGenerationResponseUsage
from ..models.content_generation_response_detected_entities_array_item_ref import (
    ContentGenerationResponseDetectedEntitiesArrayItemRef,
)
from ..models.content_generation_response_context_grounding_citations_array_item_ref import (
    ContentGenerationResponseContextGroundingCitationsArrayItemRef,
)


class ContentGenerationResponse(BaseModel):
    """
    Attributes:
        choices (Optional[list['ContentGenerationResponseChoicesArrayItemRef']]):
        context_grounding_citations (Optional[list['ContentGenerationResponseContextGroundingCitationsArrayItemRef']]):
        context_grounding_citations_string (Optional[str]): The Context grounding citations string Example:
                [{"reference":"","source":"OP2_MedLM_Results.pdf","page_number":0}].
        created (Optional[int]): The Created Example: 1.709197578E9.
        detected_entities (Optional[list['ContentGenerationResponseDetectedEntitiesArrayItemRef']]):
        id (Optional[str]): The ID Example: chatcmpl-8xWeoCeGSDzgCUaMs3edg3X6n78PP.
        masked_text (Optional[str]): This field represents the input prompt where any potential PII data has been
                replaced with masked placeholders. Example: You are tasked with drafting a notification email to inform
                individuals about a data breach incident involving Personally Identifiable Information (PII). The breach
                involved unauthorized access to a database containing customer records. Use the following sample PII data to
                create a realistic notification email: Sample PII data: Name: Person-336 Date of Birth: DateTime-362 Social
                Security Number (SSN): 123-45-6789 Address: Address-429 Email: Email-466 Phone Number: PhoneNumber-503 Draft an
                email to notify affected individuals about the breach, reassure them of steps being taken to address the issue,
                and provide guidance on protecting their information. Ensure that the email is clear, concise, and empathetic..
        model (Optional[str]): The name or ID of the model or deployment to use for the chat completion Example:
                gpt-4o-mini-2024-07-18.
        object_ (Optional[str]): The Object Example: chat.completion.
        text (Optional[str]): The Text Example: UiPath is widely considered to be the leading organization in the field
                of Robotic Process Automation (RPA). It offers a comprehensive RPA platform that enables businesses to automate
                repetitive tasks, streamline processes, and improve operational efficiency. UiPath has gained significant.
        usage (Optional[ContentGenerationResponseUsage]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    choices: Optional[list["ContentGenerationResponseChoicesArrayItemRef"]] = Field(
        alias="choices", default=None
    )
    context_grounding_citations: Optional[
        list["ContentGenerationResponseContextGroundingCitationsArrayItemRef"]
    ] = Field(alias="contextGroundingCitations", default=None)
    context_grounding_citations_string: Optional[str] = Field(
        alias="contextGroundingCitationsString", default=None
    )
    created: Optional[int] = Field(alias="created", default=None)
    detected_entities: Optional[
        list["ContentGenerationResponseDetectedEntitiesArrayItemRef"]
    ] = Field(alias="detectedEntities", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    masked_text: Optional[str] = Field(alias="maskedText", default=None)
    model: Optional[str] = Field(alias="model", default=None)
    object_: Optional[str] = Field(alias="object", default=None)
    text: Optional[str] = Field(alias="text", default=None)
    usage: Optional["ContentGenerationResponseUsage"] = Field(
        alias="usage", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ContentGenerationResponse"], src_dict: Dict[str, Any]):
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
