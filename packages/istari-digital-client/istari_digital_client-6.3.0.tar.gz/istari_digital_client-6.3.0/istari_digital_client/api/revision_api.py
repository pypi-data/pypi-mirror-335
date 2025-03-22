import typing
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.models import Revision
from istari_digital_client.models import File
from istari_digital_client.models import Artifact
from istari_digital_client.models import Model
from istari_digital_client.models import to_openapi_id
from istari_digital_client.models import to_openapi_archive
from istari_digital_client.models import to_openapi_restore

from istari_digital_client.openapi_client.api_client import ApiClient
from istari_digital_client.openapi_client.api.revision_api import (
    RevisionApi as OpenApiRevisionApi,
)

if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client


class RevisionApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_revision_api = OpenApiRevisionApi(api_client)
        self.client = client

    def get_revision(self, revision_id: str | UUID | Revision) -> Revision:
        openapi_revision = self.openapi_revision_api.get_revision(
            revision_id=to_openapi_id(revision_id, Revision)
        )
        return Revision(openapi_revision, self.client)

    def archive_revision(
        self, revision_id: str | UUID | Revision, reason: str | None = None
    ) -> Revision:
        openapi_revision = self.openapi_revision_api.archive_file_revision(
            to_openapi_id(revision_id, Revision),
            archive=to_openapi_archive(reason),
        )
        return Revision(openapi_revision, self.client)

    def restore_revision(
        self, revision_id: str | UUID | Revision, reason: str | None = None
    ) -> Revision:
        openapi_revision = self.openapi_revision_api.restore_file_revision(
            to_openapi_id(revision_id, Revision),
            restore=to_openapi_restore(reason),
        )
        return Revision(openapi_revision, self.client)

    def copy_revision_to_new_file(self, revision_id: str | UUID | Revision) -> File:
        openapi_file = self.openapi_revision_api.copy_revision_to_new_file(
            to_openapi_id(revision_id, Revision)
        )
        return File(openapi_file, self.client)

    def copy_revision_to_existing_file(
        self, *, revision_id: str | UUID | Revision, file_id: str | UUID | File
    ) -> File:
        openapi_file = self.openapi_revision_api.transfer_revision_to_existing_file(
            revision_id=to_openapi_id(revision_id, Revision),
            file_id=to_openapi_id(file_id, File),
        )
        return File(openapi_file, self.client)

    def transfer_revision_to_new_file(self, revision_id: str | UUID | Revision) -> File:
        openapi_file = self.openapi_revision_api.transfer_revision_to_new_file(
            to_openapi_id(revision_id, Revision)
        )

        return File(openapi_file, self.client)

    def transfer_revision_to_existing_file(
        self, *, revision_id: str | UUID | Revision, file_id: str | UUID | File
    ) -> File:
        openapi_file = self.openapi_revision_api.transfer_revision_to_existing_file(
            revision_id=to_openapi_id(revision_id, Revision),
            file_id=to_openapi_id(file_id, File),
        )

        return File(openapi_file, self.client)

    def transfer_revision_to_new_artifact(
        self, revision_id: str | UUID | Revision, model_id: str | UUID | Model
    ) -> Revision:
        openapi_revision = self.openapi_revision_api.transfer_revision_to_new_artifact(
            revision_id=to_openapi_id(revision_id, Revision),
            model_id=to_openapi_id(model_id, Model),
        )

        return Revision(openapi_revision, self.client)

    def transfer_revision_to_existing_artifact(
        self, *, revision_id: str | UUID | Revision, artifact_id: str | UUID | Artifact
    ) -> Revision:
        openapi_revision = (
            self.openapi_revision_api.transfer_revision_to_existing_artifact(
                revision_id=to_openapi_id(revision_id, Revision),
                artifact_id=to_openapi_id(artifact_id, Artifact),
            )
        )

        return Revision(openapi_revision, self.client)
