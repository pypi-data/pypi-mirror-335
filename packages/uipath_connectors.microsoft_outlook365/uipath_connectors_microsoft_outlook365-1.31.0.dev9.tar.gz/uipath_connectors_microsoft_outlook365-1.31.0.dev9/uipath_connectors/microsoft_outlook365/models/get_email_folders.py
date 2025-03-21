from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetEmailFolders(BaseModel):
    """
    Attributes:
        child_folder_count (Optional[float]):
        display_name (Optional[str]):
        id (Optional[str]):
        is_folder (Optional[bool]):
        is_hidden (Optional[bool]):
        parent_folder_id (Optional[str]):
        total_item_count (Optional[float]):
        unread_item_count (Optional[float]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    child_folder_count: Optional[float] = Field(alias="childFolderCount", default=None)
    display_name: Optional[str] = Field(alias="displayName", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_folder: Optional[bool] = Field(alias="isFolder", default=None)
    is_hidden: Optional[bool] = Field(alias="isHidden", default=None)
    parent_folder_id: Optional[str] = Field(alias="parentFolderId", default=None)
    total_item_count: Optional[float] = Field(alias="totalItemCount", default=None)
    unread_item_count: Optional[float] = Field(alias="unreadItemCount", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEmailFolders"], src_dict: Dict[str, Any]):
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
