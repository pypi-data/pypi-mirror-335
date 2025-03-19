from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.generate_email_request_output_format import (
    GenerateEmailRequestOutputFormat,
)
from ..models.generate_email_request_output_language import (
    GenerateEmailRequestOutputLanguage,
)
from ..models.generate_email_request_salutation import GenerateEmailRequestSalutation
from ..models.generate_email_request_sign_off import GenerateEmailRequestSignOff
from ..models.generate_email_request_style import GenerateEmailRequestStyle


class GenerateEmailRequest(BaseModel):
    """
    Attributes:
        email_content (str): The content to include in the email. This should be all of the things that must be included
                in the email. Example: Dear team,

                I am pleased to inform you that our project has been successfully completed ahead of schedule. This achievement
                is a testament to your hard work, dedication, and teamwork. I would like to extend my heartfelt gratitude to
                each and every one of you for your contributions and commitment to excellence.

                As we celebrate this milestone, let us continue to strive for excellence in all our endeavors. Together, we can
                overcome any challenge and achieve even greater success in the future.

                Thank you once again for your outstanding efforts.

                Best regards,
                [Your Name].
        need_salutation (bool): Include salutation if needed Example: True.
        need_sign_off (bool): Include sign-off if needed Example: True.
        creativity (Optional[float]): The value of the creativity factor or sampling temperature to use. Higher values
                means the model will take more risks.
        detect_input_language (Optional[bool]): Detect the language input and either return the email content in the
                same language or a different language
        emailContent (Optional[str]): The content of the email after translation. Example: Esteemed Colleagues,

                It is with immense pride and sincere appreciation that I share with you the remarkable news of our project’s
                early and successful completion. This significant milestone is not just a marker of success, but a resounding
                affirmation of your unparalleled commitment, unwavering dedication, and collaborative spirit which have been
                instrumental in surpassing our collective goals.

                Your individual contributions have coalesced into an extraordinary display of excellence that not only meets but
                exceeds the high standards we set for ourselves. As we take a moment to bask in the glory of our achievement,
                let it also serve as an impetus to continue pushing the boundaries of what we can accomplish. The road ahead is
                laden with opportunities to elevate our collective prowess and to carve out new echelons of success.

                May we take this success as a foundation upon which we will build ever more ambitious projects. Let the
                commendable work ethic and drive seen in this endeavor be the benchmark for all future undertakings. I am
                earnestly grateful for your formidable efforts and I look forward to our continued journey towards excellence.

                Thank you once again for your dedication and for setting a stellar example of teamwork in action.

                Warm regards,
                [Your Name].
        example (Optional[str]): Example of an email to match style and tone Example: Dear team, I am pleased to inform
                you that our project has been successfully completed ahead of schedule....
        output_language (Optional[GenerateEmailRequestOutputLanguage]): Language preference for output if not the same
                as input Example: German.
        output_format (Optional[GenerateEmailRequestOutputFormat]): The desired format for the generated email output.
                Example: Plain text.
        salutation_name (Optional[str]): Name to use with salutation greeting Example: Bubba.
        salutation_string (Optional[GenerateEmailRequestSalutation]): Type a custom salutation or use a value in the
                dropdown Example: Hello.
        sign_off_name (Optional[str]): The name to sign-off with.
        sign_off_string (Optional[GenerateEmailRequestSignOff]): Type a custom sign-off or use a value in the dropdown
                Example: None.
        style (Optional[GenerateEmailRequestStyle]): The style of writing to output. Example: Persuasive.
        total_words (Optional[int]): Approximate number of words to return. If not populated, model will determine
                appropriate length Example: 250.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    email_content: str = Field(alias="email_content")
    need_salutation: bool = Field(alias="need_salutation")
    need_sign_off: bool = Field(alias="need_sign_off")
    creativity: Optional[float] = Field(alias="creativity", default=None)
    detect_input_language: Optional[bool] = Field(
        alias="detectInputLanguage", default=None
    )
    emailContent: Optional[str] = Field(alias="emailContent", default=None)
    example: Optional[str] = Field(alias="example", default=None)
    output_language: Optional[GenerateEmailRequestOutputLanguage] = Field(
        alias="outputLanguage", default=None
    )
    output_format: Optional[GenerateEmailRequestOutputFormat] = Field(
        alias="output_format", default=None
    )
    salutation_name: Optional[str] = Field(alias="salutation_name", default=None)
    salutation_string: Optional[GenerateEmailRequestSalutation] = Field(
        alias="salutation_string", default=None
    )
    sign_off_name: Optional[str] = Field(alias="sign_off_name", default=None)
    sign_off_string: Optional[GenerateEmailRequestSignOff] = Field(
        alias="sign_off_string", default=None
    )
    style: Optional[GenerateEmailRequestStyle] = Field(alias="style", default=None)
    total_words: Optional[int] = Field(alias="total_words", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GenerateEmailRequest"], src_dict: Dict[str, Any]):
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
