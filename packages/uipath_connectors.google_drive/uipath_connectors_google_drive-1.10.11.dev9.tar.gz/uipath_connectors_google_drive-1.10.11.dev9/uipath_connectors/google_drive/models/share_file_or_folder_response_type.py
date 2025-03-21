from enum import Enum


class ShareFileOrFolderResponseType(str, Enum):
    ANYONE = "anyone"
    DOMAIN = "domain"
    GROUP = "group"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
