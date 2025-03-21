from enum import Enum


class ShareFileOrFolderRequestType(str, Enum):
    ANYONE = "anyone"
    DOMAIN = "domain"
    GROUP = "group"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
