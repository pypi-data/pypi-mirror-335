from enum import Enum


class GenerateEmailRequestSignOff(str, Enum):
    CHEERS = "Cheers"
    DEAR = "Dear"
    NONE = "None"
    REGARDS = "Regards"
    SINCERELY = "Sincerely"
    THANK_YOU = "Thank you"
    YOURS_TRULY = "Yours truly"

    def __str__(self) -> str:
        return str(self.value)
