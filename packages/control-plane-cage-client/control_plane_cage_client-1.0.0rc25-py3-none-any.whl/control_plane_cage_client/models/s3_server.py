from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.s3_server_format import S3ServerFormat
from ..types import UNSET, Unset

T = TypeVar("T", bound="S3Server")


@_attrs_define
class S3Server:
    """Data can be fetched via S3 protocol

    Attributes:
        type_ (str): Type of the server. Example: s3.
        location (str): S3 URL, starting with s3://
        endpoint_url (str): The server endpoint for S3-compatible servers, such as MioIO or Google Cloud Storage
        format_ (S3ServerFormat): Format of files
        delimeter (Union[Unset, str]): (Only for format = json), how multiple json documents are delimited within one
            file
    """

    type_: str
    location: str
    endpoint_url: str
    format_: S3ServerFormat
    delimeter: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        location = self.location

        endpoint_url = self.endpoint_url

        format_ = self.format_.value

        delimeter = self.delimeter

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "location": location,
                "endpointUrl": endpoint_url,
                "format": format_,
            }
        )
        if delimeter is not UNSET:
            field_dict["delimeter"] = delimeter

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        location = d.pop("location")

        endpoint_url = d.pop("endpointUrl")

        format_ = S3ServerFormat(d.pop("format"))

        delimeter = d.pop("delimeter", UNSET)

        s3_server = cls(
            type_=type_,
            location=location,
            endpoint_url=endpoint_url,
            format_=format_,
            delimeter=delimeter,
        )

        s3_server.additional_properties = d
        return s3_server

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
