from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetEventListBody(BaseModel):
    """
    Attributes:
        content (Optional[str]): Contains the main content or description of the event. Example: <html><head><meta http-
                equiv="Content-Type" content="text/html; charset=utf-8">
                <meta name="Generator" content="Microsoft Exchange Server">
                <!-- converted from text -->
                <style><!-- .EmailQuote { margin-left: 1pt; padding-left: 4pt; border-left: #800000 2px solid; }
                --></style></head>
                <body>
                <font size="2"><span style="font-size:11pt;"><div class="PlainText">Test update</div></span></font>
                </body>
                </html>
                .
        content_type (Optional[str]): Specifies the format of the event's body content, such as HTML or plain text.
                Example: html.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content: Optional[str] = Field(alias="content", default=None)
    content_type: Optional[str] = Field(alias="contentType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEventListBody"], src_dict: Dict[str, Any]):
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
