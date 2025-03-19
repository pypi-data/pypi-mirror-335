from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.rewrite_request_output_language import RewriteRequestOutputLanguage


class RewriteRequest(BaseModel):
    """
    Attributes:
        content_to_rewrite (str): Enter the text content you want to be rewritten Example: Protocol Buffers, also known
                as protobuf, is a method for serializing structured data. It's developed by Google and is used extensively
                within Google for communication between internal services and for data storage. It's designed to be language-
                neutral, platform-neutral, and extensible. At its core, Protocol Buffers defines a language-independent,
                platform-neutral format for serializing structured data. It allows you to define the structure of your data in a
                language-neutral way using a simple interface description language (IDL), and then generate code in various
                programming languages to easily serialize and deserialize data in that format. Key features of Protocol Buffers
                include: Language Independence: You can define your data structures in a .proto file using Protocol Buffers'
                Interface Definition Language (IDL), and then use code generation tools to generate code in multiple programming
                languages. This makes it easy to work with structured data across different programming languages and platforms.
                Efficiency: Protocol Buffers uses a binary serialization format that is more compact and efficient compared to
                text-based formats like JSON or XML. This results in smaller message sizes, faster serialization and
                deserialization, and reduced network and storage overhead. Extensibility: Protocol Buffers supports schema
                evolution, allowing you to evolve your data schema over time without breaking backward compatibility. You can
                add new fields, remove existing fields, and make other changes to your data schema while ensuring that older
                clients can still read messages serialized with the newer schema. Cross-Platform Support: Protocol Buffers
                supports a wide range of programming languages, including C++, Java, Python, Go, and more. This makes it easy to
                integrate Protocol Buffers into your existing projects and work with structured data across different platforms.
                Overall, Protocol Buffers provides a flexible, efficient, and language-independent way to serialize structured
                data, making it ideal for use cases such as inter-service communication, data storage, and API serialization..
        detect_input_language (Optional[bool]): Detect the language input and either return the rewrite in the same
                language or a different language
        example (Optional[str]): A sample of rewritten content that helps identify appropriate style and tone
        output_language (Optional[RewriteRequestOutputLanguage]): Language preference for output if not the same as
                input Example: German.
        rewrite_instructions (Optional[str]): Style guidelines for rewrite. This should be concise and focus on things
                like tone, audience, purpose, etc. Example: Rewrite in a more engaging and informative style, using simpler
                terms and focusing on key insights..
        temperature (Optional[float]): Determines the level of creativity applied to the output. A value of 0 indicates
                minimal creativity, sticking closely to the original content, while a value of 1 encourages maximum creativity,
                potentially introducing more novel rephrasings. Adjust this setting based on how closely you want the output to
                adhere to the input.
        total_words (Optional[int]): The total count of words in the output text. If not populated, model will determine
                appropriate length Example: 30.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content_to_rewrite: str = Field(alias="content_to_rewrite")
    detect_input_language: Optional[bool] = Field(
        alias="detectInputLanguage", default=None
    )
    example: Optional[str] = Field(alias="example", default=None)
    output_language: Optional[RewriteRequestOutputLanguage] = Field(
        alias="outputLanguage", default=None
    )
    rewrite_instructions: Optional[str] = Field(
        alias="rewrite_instructions", default=None
    )
    temperature: Optional[float] = Field(alias="temperature", default=None)
    total_words: Optional[int] = Field(alias="total_words", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["RewriteRequest"], src_dict: Dict[str, Any]):
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
