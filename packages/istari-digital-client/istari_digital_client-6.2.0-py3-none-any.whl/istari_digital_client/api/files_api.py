import typing
from uuid import UUID
from typing import Iterable

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client import FilesApi as OpenApiFilesApi
from istari_digital_client.openapi_client import ApiClient
from istari_digital_client.openapi_client import FilterBy

if typing.TYPE_CHECKING:
    from istari_digital_client import Client

from istari_digital_client.models import (
    File,
    FilePage,
    Revision,
    PathLike,
    to_openapi_id,
    to_new_source_list_or_none,
    ResourceLike,
    NewSource,
    to_openapi_archive,
    to_openapi_restore,
)


class FilesApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_files_api = OpenApiFilesApi(api_client)
        self.client = client

    def add_file(
        self,
        path: PathLike,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> File:
        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=to_new_source_list_or_none(sources),
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        openapi_file = self.openapi_files_api.create_file(
            file_revision=file_revision,
        )

        return File(openapi_file, self.client)

    def get_file(self, file_id: UUID | str | File) -> File:
        file_id = to_openapi_id(file_id, File)
        openapi_file = self.openapi_files_api.get_file(file_id)

        return File(openapi_file, self.client)

    def get_file_by_revision_id(self, revision_id: UUID | str | Revision) -> File:
        revision_id = to_openapi_id(revision_id, Revision)
        openapi_file = self.openapi_files_api.get_file_by_revision_id(revision_id)

        return File(openapi_file, self.client)

    def list_files(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        created_by: str | FilterBy | None = None,
    ) -> FilePage:
        if isinstance(created_by, str):
            if created_by not in ["-created_by_id", "created_by_id"]:
                raise ValueError(
                    "created_by must be either '-created_by_id' or 'created_by_id'"
                )
            created_by = FilterBy(created_by)

        openapi_page = self.openapi_files_api.list_files(
            page=page, size=size, sort=sort, filter_by=created_by
        )
        return FilePage(openapi_page, self.client)

    def update_file(
        self,
        file_id: File | UUID | str,
        path: PathLike | str,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> File:
        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=to_new_source_list_or_none(sources),
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        file_id = to_openapi_id(file_id, File)

        openapi_file = self.openapi_files_api.update_file(
            file_id=file_id,
            file_revision=file_revision,
        )

        return File(openapi_file, self.client)

    def update_file_properties(
        self,
        file: File,
        display_name: str | None = None,
        description: str | None = None,
    ) -> File:
        token_with_properties = self.client.storage.update_revision_properties(
            file=file,
            display_name=display_name,
            description=description,
        )

        file_id = to_openapi_id(file, File)

        openapi_file = self.openapi_files_api.update_file_properties(
            file_id=file_id, token_with_properties=token_with_properties
        )

        return File(openapi_file, self.client)

    def archive_file(
        self, file_id: File | UUID | str, reason: str | None = None
    ) -> File:
        return File(
            self.openapi_files_api.archive_file(
                to_openapi_id(file_id, File), archive=to_openapi_archive(reason)
            ),
            self.client,
        )

    def restore_file(
        self, file_id: File | UUID | str, reason: str | None = None
    ) -> File:
        return File(
            self.openapi_files_api.restore_file(
                to_openapi_id(file_id, File), restore=to_openapi_restore(reason)
            ),
            self.client,
        )
