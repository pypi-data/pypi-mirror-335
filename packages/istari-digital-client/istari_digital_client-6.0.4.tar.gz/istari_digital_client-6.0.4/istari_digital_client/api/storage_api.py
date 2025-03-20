import datetime
from typing import List, TYPE_CHECKING, Optional
import uuid

import istari_digital_core
from istari_digital_client.configuration import Configuration

if TYPE_CHECKING:
    from istari_digital_client import Client, ArchiveStatusName

from istari_digital_client.models import PathLike
from istari_digital_client.models import Properties
from istari_digital_client.models import NewSource
from istari_digital_client.models import File

from istari_digital_client.openapi_client.models.file_revision import FileRevision
from istari_digital_client.openapi_client.models.token import Token
from istari_digital_client.openapi_client.models.file_revision_archive_status import (
    FileRevisionArchiveStatus,
)
from istari_digital_client.openapi_client.models.archive_status_name import (
    ArchiveStatusName,
)
from istari_digital_client.openapi_client.models.source import Source
from istari_digital_client.openapi_client.models.token_with_properties import (
    TokenWithProperties,
)


class StorageApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ):
        native_configuration = config.native_configuration
        self.storage_client = istari_digital_core.Client(
            configuration=native_configuration
        )

        self.client = client

    def create_revision(
        self,
        file_path: PathLike,
        sources: list[NewSource] | None = None,
        display_name: str | None = None,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
    ) -> FileRevision:
        storage_revision = self.storage_client.create_revision(
            str(file_path),
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        if sources:
            source_list: List[Source] = [
                (
                    Source(
                        revision_id=str(source.revision_id),
                        file_id=None,
                        resource_type=None,
                        resource_id=None,
                        relationship_identifier=source.relationship_identifier,
                    )
                )
                for source in sources
            ]
        else:
            source_list = []

        return file_revision_from_storage_revision(
            storage_revision,
            sources=source_list,
        )

    def update_revision_properties(
        self,
        file: File,
        display_name: str | None = None,
        description: str | None = None,
    ) -> TokenWithProperties:
        file_revision = file.revision

        storage_properties = istari_digital_core.Properties(
            file_name=file_revision.name,
            extension=file_revision.extension,
            size=file_revision.size,
            description=description,
            mime=file_revision.mime_type,
            version_name=file_revision.version_name,
            external_identifier=file_revision.external_identifier,
            display_name=display_name,
        )

        updated_properties_token = self.storage_client.update_properties(
            properties=storage_properties,
        )

        return TokenWithProperties(
            id=str(uuid.uuid4()),
            created=datetime.datetime.now(datetime.timezone.utc),
            sha=updated_properties_token.sha,
            salt=updated_properties_token.salt,
            name=storage_properties.file_name,
            extension=storage_properties.extension,
            size=storage_properties.size,
            description=storage_properties.description,
            mime=storage_properties.mime,
            version_name=storage_properties.version_name,
            external_identifier=storage_properties.external_identifier,
            display_name=storage_properties.display_name,
        )

    def read_contents(self, token: Token) -> bytes:
        return self.storage_client.read_contents(token.sha, token.salt)

    def read_properties(self, token: Token) -> Properties:
        native_properties = self.storage_client.read_properties(token.sha, token.salt)

        return Properties(native_properties, self.client)


def file_revision_from_storage_revision(
    storage_revision: istari_digital_core.Revision,
    sources: Optional[List[Source]],
) -> FileRevision:
    file_revision_id = str(uuid.uuid4())

    file_revision_archive_status = FileRevisionArchiveStatus(
        id=str(uuid.uuid4()),
        created=datetime.datetime.now(datetime.timezone.utc),
        name=ArchiveStatusName.ACTIVE,
        reason="Initial",
        created_by_id=None,
        file_revision_id=file_revision_id,
    )

    return FileRevision(
        id=file_revision_id,
        created=datetime.datetime.now(datetime.timezone.utc),
        file_id=None,
        content_token=token_from_storage_token(storage_revision.content_token),
        properties_token=token_from_storage_token(storage_revision.properties_token),
        archive_status_history=[file_revision_archive_status],
        name=storage_revision.properties.file_name,
        extension=storage_revision.properties.extension,
        size=storage_revision.properties.size,
        description=storage_revision.properties.description,
        mime=storage_revision.properties.mime,
        version_name=storage_revision.properties.version_name,
        external_identifier=storage_revision.properties.external_identifier,
        display_name=storage_revision.properties.display_name,
        sources=sources,
        products=None,
        created_by_id=None,
    )


def token_from_storage_token(
    storage_token: istari_digital_core.Token,
) -> Token:
    return Token(
        id=str(uuid.uuid4()),
        created=datetime.datetime.now(datetime.timezone.utc),
        sha=storage_token.sha,
        salt=storage_token.salt,
    )
