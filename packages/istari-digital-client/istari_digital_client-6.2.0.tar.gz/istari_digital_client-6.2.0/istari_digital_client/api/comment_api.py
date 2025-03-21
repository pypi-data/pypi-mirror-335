import typing

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client import CommentApi as OpenApiCommentApi
from istari_digital_client.openapi_client import ApiClient

if typing.TYPE_CHECKING:
    from istari_digital_client import Client

from istari_digital_client.models import (
    Comment,
    ResourceLike,
    to_openapi_id,
    PathLike,
    to_openapi_archive,
    to_openapi_restore,
)

from uuid import UUID


class CommentApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_comment_api = OpenApiCommentApi(api_client)
        self.client = client

    def add_comment(
        self,
        resource_id: str | UUID | ResourceLike,
        path: PathLike,
        description: str | None = None,
    ) -> Comment:
        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=None,
            display_name=None,
            description=description,
            version_name=None,
            external_identifier=None,
        )

        openapi_comment = self.openapi_comment_api.create_comment(
            resource_id=to_openapi_id(resource_id, ResourceLike),
            file_revision=file_revision,
        )

        return Comment(openapi_comment, self.client)

    def get_comment(self, comment_id: str | UUID | Comment) -> Comment:
        openapi_comment = self.openapi_comment_api.get_comment(
            comment_id=to_openapi_id(comment_id, Comment)
        )

        return Comment(openapi_comment, self.client)

    def update_comment(
        self,
        comment_id: str | UUID | Comment,
        path: PathLike,
        description: str | None = None,
    ) -> Comment:
        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=None,
            display_name=None,
            description=description,
            version_name=None,
            external_identifier=None,
        )

        openapi_comment = self.openapi_comment_api.update_comment(
            comment_id=to_openapi_id(comment_id, Comment),
            file_revision=file_revision,
        )

        return Comment(openapi_comment, self.client)

    def archive_comment(
        self, comment_id: Comment | str | UUID, reason: str | None = None
    ) -> Comment:
        openapi_comment = self.openapi_comment_api.archive_comment(
            to_openapi_id(comment_id),
            archive=to_openapi_archive(reason),
        )
        return Comment(openapi_comment, self.client)

    def restore_comment(
        self, comment_id: Comment | str | UUID, reason: str | None = None
    ) -> Comment:
        openapi_comment = self.openapi_comment_api.restore_comment(
            to_openapi_id(comment_id), restore=to_openapi_restore(reason)
        )
        return Comment(openapi_comment, self.client)
