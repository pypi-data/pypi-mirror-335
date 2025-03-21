from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.upload_files_response_image_media_metadata_location import (
    UploadFilesResponseImageMediaMetadataLocation,
)


class UploadFilesResponseImageMediaMetadata(BaseModel):
    """
    Attributes:
        aperture (Optional[int]):
        camera_make (Optional[str]):
        camera_model (Optional[str]):
        color_space (Optional[str]):
        exposure_bias (Optional[int]):
        exposure_mode (Optional[str]):
        exposure_time (Optional[int]):
        flash_used (Optional[bool]):
        focal_length (Optional[int]):
        height (Optional[int]):
        iso_speed (Optional[int]):
        lens (Optional[str]):
        location (Optional[UploadFilesResponseImageMediaMetadataLocation]):
        max_aperture_value (Optional[int]):
        metering_mode (Optional[str]):
        rotation (Optional[int]):
        sensor (Optional[str]):
        subject_distance (Optional[int]):
        time (Optional[str]):
        white_balance (Optional[str]):
        width (Optional[int]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    aperture: Optional[int] = Field(alias="aperture", default=None)
    camera_make: Optional[str] = Field(alias="cameraMake", default=None)
    camera_model: Optional[str] = Field(alias="cameraModel", default=None)
    color_space: Optional[str] = Field(alias="colorSpace", default=None)
    exposure_bias: Optional[int] = Field(alias="exposureBias", default=None)
    exposure_mode: Optional[str] = Field(alias="exposureMode", default=None)
    exposure_time: Optional[int] = Field(alias="exposureTime", default=None)
    flash_used: Optional[bool] = Field(alias="flashUsed", default=None)
    focal_length: Optional[int] = Field(alias="focalLength", default=None)
    height: Optional[int] = Field(alias="height", default=None)
    iso_speed: Optional[int] = Field(alias="isoSpeed", default=None)
    lens: Optional[str] = Field(alias="lens", default=None)
    location: Optional["UploadFilesResponseImageMediaMetadataLocation"] = Field(
        alias="location", default=None
    )
    max_aperture_value: Optional[int] = Field(alias="maxApertureValue", default=None)
    metering_mode: Optional[str] = Field(alias="meteringMode", default=None)
    rotation: Optional[int] = Field(alias="rotation", default=None)
    sensor: Optional[str] = Field(alias="sensor", default=None)
    subject_distance: Optional[int] = Field(alias="subjectDistance", default=None)
    time: Optional[str] = Field(alias="time", default=None)
    white_balance: Optional[str] = Field(alias="whiteBalance", default=None)
    width: Optional[int] = Field(alias="width", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["UploadFilesResponseImageMediaMetadata"], src_dict: Dict[str, Any]
    ):
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
