from enum import Enum


class ShareFileOrFolderRequestPermission(str, Enum):
    COMMENTER = "commenter"
    OWNER = "owner"
    READER = "reader"
    WRITER = "writer"

    def __str__(self) -> str:
        return str(self.value)
