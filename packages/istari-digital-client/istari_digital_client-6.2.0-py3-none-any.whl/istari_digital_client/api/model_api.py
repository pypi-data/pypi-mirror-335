import typing
from pathlib import Path
from typing import Iterable
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client import ApiClient
from istari_digital_client.openapi_client import ModelApi as OpenApiModelApi

if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client

from istari_digital_client.models import (
    Model,
    ModelListItemPage,
    ArtifactPage,
    CommentPage,
    JobPage,
    PathLike,
    ResourceLike,
    File,
    Revision,
    StatusName,
    to_openapi_id,
    to_new_source_list_or_none,
    NewSource,
    to_openapi_archive,
    to_openapi_restore,
)

from istari_digital_client.openapi_client.models import FilterBy, ArchiveStatus
from istari_digital_client.api.utils import archive_status_from_str


class ModelApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_model_api = OpenApiModelApi(api_client)
        self.client = client

    def add_model(
        self,
        path: PathLike,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Model:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)

        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=to_new_source_list_or_none(sources),
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        # noinspection PyArgumentList
        openapi_model = self.openapi_model_api.create_model(
            file_revision=file_revision,
        )
        return Model(openapi_model, self.client)

    def update_model(
        self,
        model_id: UUID | str | Model,
        path: PathLike,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Model:
        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=to_new_source_list_or_none(sources),
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        openapi_model = self.openapi_model_api.update_model(
            model_id=to_openapi_id(model_id, Model),
            file_revision=file_revision,
        )

        return Model(openapi_model, self.client)

    def get_model(self, model_id: UUID | str | Model) -> Model:
        openapi_model = self.openapi_model_api.get_model(to_openapi_id(model_id))

        return Model(openapi_model, self.client)

    def list_models(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        created_by: str | FilterBy | None = None,
        archive_status: str | ArchiveStatus | None = None,
    ) -> ModelListItemPage:
        if isinstance(created_by, str):
            if created_by not in ["-created_by_id", "created_by_id"]:
                raise ValueError(
                    "created_by must be either '-created_by_id' or 'created_by_id'"
                )
            created_by = FilterBy(created_by)

        if isinstance(archive_status, str):
            archive_status = archive_status_from_str(archive_status)

        openapi_page = self.openapi_model_api.list_models(
            page=page,
            size=size,
            sort=sort,
            filter_by=created_by,
            archive_status=archive_status,
        )
        return ModelListItemPage(openapi_page, self.client)

    def list_model_artifacts(
        self,
        model_id: UUID | str | Model,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        created_by: str | FilterBy | None = None,
        archive_status: str | ArchiveStatus | None = None,
    ) -> ArtifactPage:
        if isinstance(created_by, str):
            if created_by not in ["-created_by_id", "created_by_id"]:
                raise ValueError(
                    "created_by must be either '-created_by_id' or 'created_by_id'"
                )
            created_by = FilterBy(created_by)

        if isinstance(archive_status, str):
            archive_status = archive_status_from_str(archive_status)

        openapi_page = self.openapi_model_api.list_model_artifacts(
            model_id=to_openapi_id(model_id, Model),
            page=page,
            size=size,
            sort=sort,
            filter_by=created_by,
            archive_status=archive_status,
        )

        return ArtifactPage(openapi_page, self.client)

    def list_model_comments(
        self,
        model_id: UUID | str | Model,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        archive_status: str | ArchiveStatus | None = None,
    ) -> CommentPage:
        if isinstance(archive_status, str):
            archive_status = archive_status_from_str(archive_status)

        openapi_page = self.openapi_model_api.list_model_comments(
            model_id=to_openapi_id(model_id, Model),
            page=page,
            size=size,
            sort=sort,
            archive_status=archive_status,
        )

        return CommentPage(openapi_page, self.client)

    def list_model_jobs(
        self,
        model_id: UUID | str | Model,
        status_name: StatusName | None = None,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        archive_status: str | ArchiveStatus | None = None,
    ) -> JobPage:
        if isinstance(archive_status, str):
            archive_status = archive_status_from_str(archive_status)

        openapi_page = self.openapi_model_api.list_model_jobs(
            model_id=to_openapi_id(model_id, Model),
            status_name=status_name,
            page=page,
            size=size,
            sort=sort,
            archive_status=archive_status,
        )

        return JobPage(openapi_page, self.client)

    def archive_model(
        self, model_id: UUID | str | Model, reason: str | None = None
    ) -> Model:
        openapi_model = self.openapi_model_api.archive_model(
            to_openapi_id(model_id, Model),
            archive=to_openapi_archive(reason),
        )
        return Model(openapi_model, self.client)

    def restore_model(
        self, model_id: UUID | str | Model, reason: str | None = None
    ) -> Model:
        openapi_model = self.openapi_model_api.restore_model(
            to_openapi_id(model_id, Model), restore=to_openapi_restore(reason)
        )
        return Model(openapi_model, self.client)
