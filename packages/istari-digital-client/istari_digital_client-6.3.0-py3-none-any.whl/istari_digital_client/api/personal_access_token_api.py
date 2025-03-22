import typing
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client.api.personal_access_tokens_api import (
    PersonalAccessTokensApi as OpenApiPersonalAccessTokensApi,
)
from istari_digital_client.openapi_client.api_client import ApiClient
from istari_digital_client.models import PersonalAccessToken
from istari_digital_client.models import PersonalAccessTokenPage

if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client


class PersonalAccessTokenApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_personal_access_token_api = OpenApiPersonalAccessTokensApi(
            api_client
        )
        self.client = client

    def create_agent_personal_access_token(
        self,
        name: str,
    ) -> PersonalAccessToken:
        openapi_personal_access_token = (
            self.openapi_personal_access_token_api.create_agent_personal_access_token(
                name=name,
            )
        )

        return PersonalAccessToken(openapi_personal_access_token)

    def create_personal_access_token(
        self,
        name: str,
    ) -> PersonalAccessToken:
        openapi_personal_access_token = (
            self.openapi_personal_access_token_api.create_personal_access_token(
                name=name,
            )
        )

        return PersonalAccessToken(openapi_personal_access_token)

    def delete_personal_access_token(
        self,
        pat_id: PersonalAccessToken | UUID | str,
    ) -> None:
        if isinstance(pat_id, PersonalAccessToken):
            pat_id = str(pat_id.id)
        if isinstance(pat_id, UUID):
            pat_id = str(pat_id)
        if isinstance(pat_id, str):
            pat_id = pat_id

        self.openapi_personal_access_token_api.delete_personal_access_token(pat_id)

    def list_personal_access_tokens(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PersonalAccessTokenPage:
        openapi_page = (
            self.openapi_personal_access_token_api.list_personal_access_tokens(
                page=page,
                size=size,
                sort=sort,
            )
        )

        return PersonalAccessTokenPage(openapi_page)

    def revoke_all_personal_access_tokens(self) -> None:
        self.openapi_personal_access_token_api.revoke_all_personal_access_tokens()
