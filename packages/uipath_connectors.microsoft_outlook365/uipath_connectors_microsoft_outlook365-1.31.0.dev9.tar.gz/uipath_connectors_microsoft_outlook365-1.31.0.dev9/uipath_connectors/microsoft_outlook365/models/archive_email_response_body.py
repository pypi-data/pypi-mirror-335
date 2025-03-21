from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class ArchiveEmailResponseBody(BaseModel):
    """
    Attributes:
        content (Optional[str]): The main content or message body of the email. Example: <html><head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8"><meta name="Generator" content="Microsoft
                Word 15 (filtered medium)"><style>
                <!--
                @font-face
                        {font-family:"Cambria Math"}
                @font-face
                        {font-family:Aptos}
                p.MsoNormal, li.MsoNormal, div.MsoNormal
                        {margin:0cm;
                        font-size:11.0pt;
                        font-family:"Aptos",sans-serif}
                span.EmailStyle17
                        {font-family:"Aptos",sans-serif;
                        color:windowtext}
                .MsoChpDefault
                        {font-size:11.0pt}
                @page WordSection1
                        {margin:72.0pt 72.0pt 72.0pt 72.0pt}
                div.WordSection1
                        {}
                -->
                </style></head><body lang="EN-IN" link="#467886" vlink="#96607D" style="word-wrap:break-word"><div
                class="WordSection1"><p class="MsoNormal"><span lang="EN-US">AttachmentInEmail</span></p></div></body></html>.
        content_type (Optional[str]): The format type of the email body content, such as HTML or plain text. Example:
                html.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content: Optional[str] = Field(alias="content", default=None)
    content_type: Optional[str] = Field(alias="contentType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ArchiveEmailResponseBody"], src_dict: Dict[str, Any]):
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
