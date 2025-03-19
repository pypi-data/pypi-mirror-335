from enum import Enum


class ShareFileOrFolderResponseShareWith(str, Enum):
    ANYONE = "anyone"
    DOMAIN = "domain"
    GROUP = "group"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
