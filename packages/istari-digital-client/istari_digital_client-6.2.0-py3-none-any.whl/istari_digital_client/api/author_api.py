import typing
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client import AuthorApi as OpenApiAuthorApi
from istari_digital_client.openapi_client import NewModuleAuthor
from istari_digital_client.openapi_client import ApiClient

from istari_digital_client.models import ModuleAuthor, ModuleAuthorPage

if typing.TYPE_CHECKING:
    from istari_digital_client import Client


class AuthorApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_author_api = OpenApiAuthorApi(api_client)
        self.client = client

    def add_author(
        self,
        name: str,
        email: str,
    ) -> ModuleAuthor:
        new_module_author = NewModuleAuthor(
            name=name,
            email=email,
        )

        openapi_author = self.openapi_author_api.create_author(
            new_module_author=new_module_author,
        )

        return ModuleAuthor(openapi_author, self.client)

    def get_author(self, author_id: UUID | str | ModuleAuthor) -> ModuleAuthor:
        if isinstance(author_id, ModuleAuthor):
            author_id = str(author_id.id)
        if isinstance(author_id, UUID):
            author_id = str(author_id)

        openapi_author = self.openapi_author_api.get_author(
            author_id=author_id,
        )

        return ModuleAuthor(openapi_author, self.client)

    def update_author(
        self,
        author_id: UUID | str | ModuleAuthor,
        name: str,
        email: str,
    ) -> ModuleAuthor:
        if isinstance(author_id, ModuleAuthor):
            author_id = str(author_id.id)
        if isinstance(author_id, UUID):
            author_id = str(author_id)

        new_module_author = NewModuleAuthor(
            name=name,
            email=email,
        )

        openapi_author = self.openapi_author_api.update_author(
            author_id=author_id,
            new_module_author=new_module_author,
        )

        return ModuleAuthor(openapi_author, self.client)

    def list_authors(
        self,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> ModuleAuthorPage:
        openapi_author_page = self.openapi_author_api.list_authors(
            page=page,
            size=size,
            sort=sort,
        )

        return ModuleAuthorPage(openapi_author_page, self.client)
