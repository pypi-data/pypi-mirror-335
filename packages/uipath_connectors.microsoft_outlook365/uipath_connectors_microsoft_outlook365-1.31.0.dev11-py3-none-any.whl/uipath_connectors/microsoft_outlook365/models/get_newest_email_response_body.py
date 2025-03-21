from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetNewestEmailResponseBody(BaseModel):
    """
    Attributes:
        content (Optional[str]): The main content or message of the email. Example: <html><head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8"><style>
                <!--
                body, p, td
                        {font-family:Verdana,Arial,Helvetica,sans-serif;
                        font-size:11px}
                -->
                </style></head><body>new comment <hr tabindex="-1" style="display:inline-block; width:98%"><div
                id="divRplyFwdMsg" dir="ltr"><font face="Calibri, sans-serif" color="#000000" style="font-
                size:11pt"><b>From:</b> UiPath INC (Development Account 18) (cedeveloper@uipath.com) &lt;system@sent-
                via.netsuite.com&gt;<br><b>Sent:</b> Wednesday, January 22, 2025 6:31:30 AM<br><b>To:</b> CE Developer
                &lt;CEdeveloper@uipath.com&gt;<br><b>Subject:</b> Case # 4738 Created: dUluNp (originally To:
                tylerperez@example.org) (originally envelope recipients: tylerperez@example.org)</font>
                <div>&nbsp;</div></div><div><p><img src="" border="0"></p><table width="100%" border="0" cellspacing="2"
                cellpadding="2"><tbody><tr valign="top"><td colspan="2" valign="top"><p>Thank you for contacting UiPath INC
                (Development Account 18) Customer Support.</p><p>Your request for assistance has been received. Case #4738 -
                &quot;dUluNp&quot; has been created for you. A member of our customer care team will respond to your case as
                soon as possible.</p><p><font style="font-size:9px; font-family:Verdana,Arial,Helvetica,sans-serif"><br><img
                src="http://content.netsuite.com/images/icons/crm/icon_updateCase.gif" align="absbottom"><a href="https://eur02.
                safelinks.protection.outlook.com/?url=https%3A%2F%2F2144368.app.netsuite.com%2Fapp%2Fsite%2Fcrm%2Fexternalcasere
                sponsepage.nl%3Fe%3DT%26compid%3D2144368%26id%3D223583%26h%3DAAFdikaIW-5KKZIVodab0LNm7Ahf1yrH-
                9JuyvBJftaKzGgIOrI&amp;data=05%7C02%7Charish.reddy%40uipath.com%7C3cd182e2e3994fe4db0c08dd3aae72ff%7Cd8353d2ab15
                34d178827902c51f72357%7C0%7C0%7C638731243105427372%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuM
                DAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&amp;sdata=p1DkpPftFEJaV2lLPhRtAN677aiz5UDqT
                1%2BVx%2B7uAJQ%3D&amp;reserved=0" originalsrc="https://2144368.app.netsuite.com/app/site/crm/externalcaserespons
                epage.nl?e=T&amp;compid=2144368&amp;id=223583&amp;h=AAFdikaIW-5KKZIVodab0LNm7Ahf1yrH-9JuyvBJftaKzGgIOrI" shash="
                DeqKM/vqbUUHppld1okEFMenZCI43mqXacBb6ta7d/xJM5I8Si3bFcR1jixzsrGR3m14bjoreAMy6WwYg2is6iloLMY/NMd+KXNGaf4afgLmAvOL
                NFxO5Y0FFiKnTa1vYRMBLMSq6G0q3q4OXg+2BKvh9VYeLgAIMaRVEOlPrHs=">Click here to update the Case online</a><font
                color="#666666">, or reply to this email</p></font></font></td></tr></tbody></table><hr width="100%" size="1"
                noshade="" color="#CCCCCC"><blockquote><p><b>Message History</b><br><font color="#666666">lKOACD
                </font></p></blockquote><hr width="100%" size="1" noshade="" color="#CCCCCC"><table width="100%" border="0"
                cellspacing="0" cellpadding="0"><tbody><tr><td align="right"><font style="font-size:9px; font-
                family:Verdana,Arial,Helvetica,sans-serif; color:#999999">UiPath INC (Development Account 18) is powered by <a h
                ref="https://eur02.safelinks.protection.outlook.com/?url=http%3A%2F%2Fwww.netsuite.com%2F&amp;data=05%7C02%7Char
                ish.reddy%40uipath.com%7C3cd182e2e3994fe4db0c08dd3aae72ff%7Cd8353d2ab1534d178827902c51f72357%7C0%7C0%7C638731243
                105448698%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIl
                dUIjoyfQ%3D%3D%7C0%7C%7C%7C&amp;sdata=2buDXD%2FUjwa7M3TQd8Gir3WMqqMfcEbJhRau6YFgmn0%3D&amp;reserved=0"
                originalsrc="http://www.netsuite.com/" shash="d19pYcvWfSgyZP+k4eo3oMI0K6tNw8IbJHUBQIjb+ZbWbhkt0ye1yeCJ/XA4rbF333
                gKjR0dFI631fAZ9ukcx/l5N3SrH4bRdt4GM71pjL8P3YXsLI+Ilodiil7l3e/s7oG9fuesAi5EvR0o0xZ32BBPeIdKnm5XnZsbKY0E90c="
                style="color:#999999">NetSuite</a> — One System. No Limits.</font>
                </td></tr></tbody></table></div></body></html>.
        content_type (Optional[str]): The format type of the email body, such as HTML or plain text. Example: html.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content: Optional[str] = Field(alias="content", default=None)
    content_type: Optional[str] = Field(alias="contentType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetNewestEmailResponseBody"], src_dict: Dict[str, Any]):
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
