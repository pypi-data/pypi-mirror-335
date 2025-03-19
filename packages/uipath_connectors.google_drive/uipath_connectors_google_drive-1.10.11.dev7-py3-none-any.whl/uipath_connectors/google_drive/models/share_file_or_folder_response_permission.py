from enum import Enum


class ShareFileOrFolderResponsePermission(str, Enum):
    COMMENTER = "commenter"
    OWNER = "owner"
    READER = "reader"
    WRITER = "writer"

    def __str__(self) -> str:
        return str(self.value)
