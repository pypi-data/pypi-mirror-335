from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GenerateEmailResponse(BaseModel):
    """
    Attributes:
        email_content (Optional[str]): The content of the email after translation. Example: Esteemed Colleagues,

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
        need_salutation (Optional[bool]): Include salutation if needed Example: True.
        need_sign_off (Optional[bool]): Include sign-off if needed Example: True.
        total_words (Optional[int]): Approximate number of words to return. If not populated, model will determine
                appropriate length Example: 250.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    email_content: Optional[str] = Field(alias="emailContent", default=None)
    need_salutation: Optional[bool] = Field(alias="need_salutation", default=None)
    need_sign_off: Optional[bool] = Field(alias="need_sign_off", default=None)
    total_words: Optional[int] = Field(alias="total_words", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GenerateEmailResponse"], src_dict: Dict[str, Any]):
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
