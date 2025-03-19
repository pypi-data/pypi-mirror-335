from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_email_type import ListEmailType
from ..models.list_email_parent_folders_array_item_ref import (
    ListEmailParentFoldersArrayItemRef,
)
from ..models.list_email_to_array_item_ref import ListEmailToArrayItemRef
from ..models.list_email_from import ListEmailFrom
from ..models.list_email_bcc_array_item_ref import ListEmailBCCArrayItemRef
from ..models.list_email_cc_array_item_ref import ListEmailCCArrayItemRef
from ..models.list_email_categories_array_item_ref import (
    ListEmailCategoriesArrayItemRef,
)


class ListEmail(BaseModel):
    """
    Attributes:
        bcc (Optional[list['ListEmailBCCArrayItemRef']]):
        cc (Optional[list['ListEmailCCArrayItemRef']]):
        categories (Optional[list['ListEmailCategoriesArrayItemRef']]):
        from_ (Optional[ListEmailFrom]):
        has_attachments (Optional[bool]):  Example: true.
        id (Optional[str]):  Example: 184e63ea8560e37d.
        parent_folders (Optional[list['ListEmailParentFoldersArrayItemRef']]):
        subject (Optional[str]):  Example: Test email with attachment.
        thread_id (Optional[str]):  Example: 184e63ea8560e37d.
        to (Optional[list['ListEmailToArrayItemRef']]):
        type_ (Optional[ListEmailType]):  Example: email.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bcc: Optional[list["ListEmailBCCArrayItemRef"]] = Field(alias="BCC", default=None)
    cc: Optional[list["ListEmailCCArrayItemRef"]] = Field(alias="CC", default=None)
    categories: Optional[list["ListEmailCategoriesArrayItemRef"]] = Field(
        alias="Categories", default=None
    )
    from_: Optional["ListEmailFrom"] = Field(alias="From", default=None)
    has_attachments: Optional[bool] = Field(alias="HasAttachments", default=None)
    id: Optional[str] = Field(alias="ID", default=None)
    parent_folders: Optional[list["ListEmailParentFoldersArrayItemRef"]] = Field(
        alias="ParentFolders", default=None
    )
    subject: Optional[str] = Field(alias="Subject", default=None)
    thread_id: Optional[str] = Field(alias="ThreadID", default=None)
    to: Optional[list["ListEmailToArrayItemRef"]] = Field(alias="To", default=None)
    type_: Optional[ListEmailType] = Field(alias="Type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListEmail"], src_dict: Dict[str, Any]):
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
