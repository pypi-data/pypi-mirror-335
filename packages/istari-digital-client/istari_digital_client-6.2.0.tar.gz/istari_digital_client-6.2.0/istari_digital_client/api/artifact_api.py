import typing
from typing import Iterable
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client import ApiClient
from istari_digital_client.openapi_client import ArtifactApi as OpenApiArtifactApi

if typing.TYPE_CHECKING:
    from istari_digital_client import Client
from istari_digital_client.openapi_client.models import FilterBy
from istari_digital_client.models import (
    Artifact,
    ArtifactPage,
    CommentPage,
    Model,
    PathLike,
    ResourceLike,
    File,
    Revision,
    to_openapi_id,
    to_new_source_list_or_none,
    NewSource,
    to_openapi_archive,
    to_openapi_restore,
)


class ArtifactApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_artifact_api = OpenApiArtifactApi(api_client)
        self.client: "Client" = client

    def add_artifact(
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
    ) -> Artifact:
        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=to_new_source_list_or_none(sources),
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        openapi_artifact = self.openapi_artifact_api.create_artifact(
            model_id=to_openapi_id(model_id, Model),
            file_revision=file_revision,
        )

        return Artifact(openapi_artifact, self.client)

    def get_artifact(self, artifact_id: str | UUID) -> Artifact:
        openapi_artifact = self.openapi_artifact_api.get_artifact(
            to_openapi_id(artifact_id, Artifact)
        )

        return Artifact(openapi_artifact, self.client)

    def update_artifact(
        self,
        artifact_id: Artifact | UUID | str,
        path: PathLike,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> Artifact:
        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=to_new_source_list_or_none(sources),
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        openapi_artifact = self.openapi_artifact_api.update_artifact(
            artifact_id=to_openapi_id(artifact_id, Artifact),
            file_revision=file_revision,
        )

        # noinspection PyArgumentList
        return Artifact(openapi_artifact, self.client)

    def list_artifacts(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        created_by: str | FilterBy | None = None,
    ) -> ArtifactPage:
        if isinstance(created_by, str):
            if created_by not in ["-created_by_id", "created_by_id"]:
                raise ValueError(
                    "created_by must be either '-created_by_id' or 'created_by_id'"
                )
            created_by = FilterBy(created_by)

        openapi_artifacts = self.openapi_artifact_api.list_artifacts(
            page=page,
            size=size,
            sort=sort,
            filter_by=created_by,
        )

        return ArtifactPage(openapi_artifacts, self.client)

    def list_artifact_comments(
        self,
        artifact_id: str | UUID | Artifact,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> CommentPage:
        artifact_id = to_openapi_id(artifact_id, Artifact)

        openapi_comment_page = self.openapi_artifact_api.list_artifact_comments(
            artifact_id=artifact_id,
            page=page,
            size=size,
            sort=sort,
        )

        return CommentPage(openapi_comment_page, self.client)

    def archive_artifact(
        self, artifact_id: Artifact | str | UUID, reason: str | None = None
    ) -> Artifact:
        openapi_artifact = self.openapi_artifact_api.archive_artifact(
            to_openapi_id(artifact_id),
            archive=to_openapi_archive(reason),
        )
        return Artifact(openapi_artifact, self.client)

    def restore_artifact(
        self, artifact_id: Artifact | str | UUID, reason: str | None = None
    ) -> Artifact:
        openapi_artifact = self.openapi_artifact_api.restore_artifact(
            to_openapi_id(artifact_id),
            restore=to_openapi_restore(reason),
        )
        return Artifact(openapi_artifact, self.client)
