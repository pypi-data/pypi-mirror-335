from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.reformat_request_input_format import ReformatRequestInputFormat
from ..models.reformat_request_output_format import ReformatRequestOutputFormat


class ReformatRequest(BaseModel):
    """
    Attributes:
        content_to_be_reformatted (str): String representation of the content to be reformatted from its original format
                into a different format.  This can also correct malformatted inputs (ex. JSON to JSON). Example: name,age
                manas,28
                krishna,29
                .
        output_format (ReformatRequestOutputFormat): The output format Example: JSON.
        example_schema (Optional[str]): Example of an output with proper format Example: [{<name>: <age>}].
        input_type (Optional[ReformatRequestInputFormat]): The input format.  This field is optional and the activity
                will automatically detect if not set. Example: CSV.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content_to_be_reformatted: str = Field(alias="contentToBeReformatted")
    output_format: ReformatRequestOutputFormat = Field(alias="outputFormat")
    example_schema: Optional[str] = Field(alias="exampleSchema", default=None)
    input_type: Optional[ReformatRequestInputFormat] = Field(
        alias="inputType", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ReformatRequest"], src_dict: Dict[str, Any]):
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
