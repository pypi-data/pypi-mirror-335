import json
from io import BytesIO
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, Unset

T = TypeVar("T", bound="BodyProjectsProjectsuploadDocuments")


@_attrs_define
class BodyProjectsProjectsuploadDocuments:
    """
    Attributes:
        files (list[File]):
        overwrite (Union[Unset, bool]):  Default: True.
        country (Union[Unset, str]):  Default: 'México'.
    """

    files: list[File]
    overwrite: Union[Unset, bool] = True
    country: Union[Unset, str] = "México"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            files.append(files_item)

        overwrite = self.overwrite

        country = self.country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if overwrite is not UNSET:
            field_dict["overwrite"] = overwrite
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    def to_multipart(self) -> dict[str, Any]:
        _temp_files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            _temp_files.append(files_item)
        files = (None, json.dumps(_temp_files).encode(), "application/json")

        overwrite = (
            self.overwrite if isinstance(self.overwrite, Unset) else (None, str(self.overwrite).encode(), "text/plain")
        )

        country = self.country if isinstance(self.country, Unset) else (None, str(self.country).encode(), "text/plain")

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = (None, str(prop).encode(), "text/plain")

        field_dict.update(
            {
                "files": files,
            }
        )
        if overwrite is not UNSET:
            field_dict["overwrite"] = overwrite
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = File(payload=BytesIO(files_item_data))

            files.append(files_item)

        overwrite = d.pop("overwrite", UNSET)

        country = d.pop("country", UNSET)

        body_projects_projectsupload_documents = cls(
            files=files,
            overwrite=overwrite,
            country=country,
        )

        body_projects_projectsupload_documents.additional_properties = d
        return body_projects_projectsupload_documents

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
