from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.summarise_text_new_request_output_language import (
    SummariseTextNewRequestOutputLanguage,
)
from ..models.summarise_text_new_request_summary_format import (
    SummariseTextNewRequestSummaryFormat,
)


class SummariseTextNewRequest(BaseModel):
    """
    Attributes:
        prompt (str): The text to summarize Example: If requestBody['instruction'] is an empty string, null, or
                undefined, the result of the expression if(requestBody['instruction']) will be false.In JavaScript, empty
                strings, null, and undefined are considered falsy values. Therefore, the condition
                if(requestBody['instruction']) will evaluate to false if requestBody['instruction'] is any of these falsy
                values, and the code block within the if statement will not be executed..
        detect_input_language (Optional[bool]): Detect the language input and either return the summary in the same
                language or a different language
        max_word_count (Optional[int]): The maximum word count for the summary of the provided text. If not populated,
                model will determine appropriate length
        output_language (Optional[SummariseTextNewRequestOutputLanguage]): Language preference for output if not the
                same as input Example: German.
        summary_format (Optional[SummariseTextNewRequestSummaryFormat]): The format for the generated summarized text,
                e.g., organized in paragraph form or as a bulleted item list, etc. Example: paragraph.
        temperature (Optional[float]): A number between 0.0 and 2.0 indicating the creativity factor or sampling
                temperature to use. Higher values means the model will be more creative with the summarization, but also take
                more risks, which could lead to more variance from the input text to summarize. Defaults to 0.5
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    prompt: str = Field(alias="prompt")
    detect_input_language: Optional[bool] = Field(
        alias="detectInputLanguage", default=None
    )
    max_word_count: Optional[int] = Field(alias="maxWordCount", default=None)
    output_language: Optional[SummariseTextNewRequestOutputLanguage] = Field(
        alias="outputLanguage", default=None
    )
    summary_format: Optional[SummariseTextNewRequestSummaryFormat] = Field(
        alias="summaryFormat", default=None
    )
    temperature: Optional[float] = Field(alias="temperature", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SummariseTextNewRequest"], src_dict: Dict[str, Any]):
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
