from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetEventListCalendarodata(BaseModel):
    """
    Attributes:
        association_link (Optional[str]): Provides a link to associate the calendar with other resources. Example: https
                ://graph.microsoft.com/v1.0/users('dfed9647-6382-4306-be51-
                0b2e0ae176a8')/calendars('AAMkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNABGAAAAAACheKuSte_nRYh5zSjSpULXBw
                B8H2U_2gSPS6CGFwCo8hoKAAAAAAEGAAB8H2U_2gSPS6CGFwCo8hoKAAAAm-qXAAA=')/$ref.
        navigation_link (Optional[str]): URL link to navigate to the calendar associated with the event. Example: https:
                //graph.microsoft.com/v1.0/users('dfed9647-6382-4306-be51-
                0b2e0ae176a8')/calendars('AAMkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNABGAAAAAACheKuSte_nRYh5zSjSpULXBw
                B8H2U_2gSPS6CGFwCo8hoKAAAAAAEGAAB8H2U_2gSPS6CGFwCo8hoKAAAAm-qXAAA=').
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    association_link: Optional[str] = Field(alias="associationLink", default=None)
    navigation_link: Optional[str] = Field(alias="navigationLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEventListCalendarodata"], src_dict: Dict[str, Any]):
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
