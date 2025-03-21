from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class CreateOnlineTeamsMeetingResponseJoinInformation(BaseModel):
    """
    Attributes:
        content (Optional[str]): Contains the content details for joining the meeting. Example:
                data:text/html,%3cdiv+style%3d%22max-width%3a+520px%3b+color%3a+%23242424%3b+font-
                family%3a%27Segoe+UI%27%2c%27Helvetica+Neue%27%2cHelvetica%2cArial%2csans-serif%22+class%3d%22me-email-
                text%22%3e%0d%0a++%3cdiv+style%3d%22margin-bottom%3a24px%3boverflow%3ahidden%3bwhite-space%3anowrap%3b%22%3e____
                ____________________________________________________________________________%3c%2fdiv%3e%0d%0a%0d%0a++%3cdiv+sty
                le%3d%22margin-bottom%3a+12px%3b%22%3e%0d%0a++++%3cspan+class%3d%22me-email-text%22+style%3d%22font-
                size%3a+24px%3bfont-weight%3a+700%3b+margin-right%3a12px%3b%22%3eMicrosoft+Teams%3c%2fspan%3e%0d%0a++++%3ca+id%3
                d%22meet_invite_block.action.help%22+class%3d%22me-email-link%22+style%3d%22font-size%3a14px%3b+text-decoration%
                3aunderline%3b+color%3a+%235B5FC7%3b%22+href%3d%22https%3a%2f%2faka.ms%2fJoinTeamsMeeting%3fomkt%3den-
                US%22%3eNeed+help%3f%3c%2fa%3e%0d%0a++%3c%2fdiv%3e%0d%0a%0d%0a++%3cdiv+style%3d%22margin-
                bottom%3a+6px%3b%22%3e%0d%0a++++%3ca+id%3d%22meet_invite_block.action.join_link%22+class%3d%22me-email-
                headline%22+style%3d%22font-size%3a+20px%3b+font-weight%3a600%3b+text-
                decoration%3a+underline%3b+color%3a+%235B5FC7%3b%22+href%3d%22https%3a%2f%2fteams.microsoft.com%2fl%2fmeetup-joi
                n%2f19%253ameeting_NzM1NmIyZmMtMTdmNy00ZTUwLThmNzUtNzEzMmQ4YjlkNTU4%2540thread.v2%2f0%3fcontext%3d%257b%2522Tid%
                2522%253a%25222999126d-261b-4dfd-a3fb-65e7cd9a4db0%2522%252c%2522Oid%2522%253a%252211847e94-4927-4a2d-8a48-
                c4658959d883%2522%257d%22+target%3d%22_blank%22+rel%3d%22noreferrer+noopener%22%3eJoin+the+meeting+now%3c%2fa%3e
                %0d%0a++%3c%2fdiv%3e%0d%0a%0d%0a++%3cdiv+style%3d%22margin-
                bottom%3a+6px%3b%22%3e%0d%0a++++%3cspan+class%3d%22me-email-text-secondary%22+style%3d%22font-
                size%3a+14px%3b+color%3a+%23616161%3b%22%3eMeeting+ID%3a+%3c%2fspan%3e%0d%0a++++%3cspan+class%3d%22me-email-
                text%22+style%3d%22font-size%3a+14px%3b+color%3a+%23242424%3b%22%3e231+045+254+323%3c%2fspan%3e%0d%0a++%3c%2fdiv
                %3e%0d%0a%0d%0a++%3cdiv+style%3d%22margin-bottom%3a+24px%3b%22%3e%0d%0a++++%3cspan+class%3d%22me-email-text-
                secondary%22+style%3d%22font-
                size%3a+14px%3b+color%3a+%23616161%3b%22%3ePasscode%3a+%3c%2fspan%3e%0d%0a++++%3cspan+class%3d%22me-email-
                text%22+style%3d%22font-size%3a+14px%3b+color%3a+%23242424%3b%22%3emKBhMi%3c%2fspan%3e%0d%0a++%3c%2fdiv%3e%0d%0a
                %0d%0a++%3cdiv+style%3d%22margin-bottom%3a+24px%3b+max-width%3a+532px%3b%22%3e%0d%0a++++%3chr+style%3d%22border%
                3a+0%3b+background%3a+%23D1D1D1%3b+height%3a+1px%3b%22%3e%3c%2fhr%3e%0d%0a++%3c%2fdiv%3e%0d%0a%0d%0a%0d%0a%0d%0a
                %0d%0a%0d%0a++%3cdiv%3e%0d%0a++++%3cspan+class%3d%22me-email-text-secondary%22+style%3d%22font-size%3a+14px%3b+c
                olor%3a+%23616161%3b%22%3eFor+organizers%3a+%3c%2fspan%3e%0d%0a++++%3ca+id%3d%22meet_invite_block.action.organiz
                er_meet_options%22+class%3d%22me-email-link%22+style%3d%22font-size%3a+14px%3b+text-decoration%3a+underline%3b+c
                olor%3a+%235B5FC7%3b%22+target%3d%22_blank%22+href%3d%22https%3a%2f%2fteams.microsoft.com%2fmeetingOptions%2f%3f
                organizerId%3d11847e94-4927-4a2d-8a48-c4658959d883%26tenantId%3d2999126d-261b-4dfd-a3fb-
                65e7cd9a4db0%26threadId%3d19_meeting_NzM1NmIyZmMtMTdmNy00ZTUwLThmNzUtNzEzMmQ4YjlkNTU4%40thread.v2%26messageId%3d
                0%26language%3den-US%22+rel%3d%22noreferrer+noopener%22%3eMeeting+options%3c%2fa%3e%0d%0a++++%3cspan+style%3d%22
                color%3a+%23D1D1D1%22%3e%7c%3c%2fspan%3e%0d%0a++++%3ca+id%3d%22meet_invite_block.action.organizer_reset_dialin_p
                in%22+class%3d%22me-email-link%22+style%3d%22font-size%3a+14px%3b+text-decoration%3a+underline%3b+color%3a+%235B
                5FC7%3b%22+target%3d%22_blank%22+href%3d%22https%3a%2f%2fdialin.teams.microsoft.com%2fusp%2fpstnconferencing%22+
                rel%3d%22noreferrer+noopener%22%3eReset+dial-
                in+PIN%3c%2fa%3e%0d%0a++%3c%2fdiv%3e%0d%0a%0d%0a++%3cdiv+style%3d%22margin-top%3a+24px%3b+margin-
                bottom%3a+6px%3b%22%3e%0d%0a++++%0d%0a++++%0d%0a++%3c%2fdiv%3e%0d%0a%0d%0a++%3cdiv+style%3d%22margin-
                bottom%3a+24px%3b%22%3e%0d%0a++++%0d%0a++%3c%2fdiv%3e%0d%0a%0d%0a++%3cdiv+style%3d%22margin-
                bottom%3a24px%3boverflow%3ahidden%3bwhite-space%3anowrap%3b%22%3e_______________________________________________
                _________________________________%3c%2fdiv%3e%0d%0a%0d%0a%3c%2fdiv%3e.
        content_type (Optional[str]): Specifies the content type of the event's join information. Example: html.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content: Optional[str] = Field(alias="content", default=None)
    content_type: Optional[str] = Field(alias="contentType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateOnlineTeamsMeetingResponseJoinInformation"],
        src_dict: Dict[str, Any],
    ):
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
