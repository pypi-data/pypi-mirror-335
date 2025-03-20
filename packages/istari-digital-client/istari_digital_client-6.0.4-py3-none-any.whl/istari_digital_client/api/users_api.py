import typing
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client.api.users_api import (
    UsersApi as OpenApiUsersApi,
)
from istari_digital_client.openapi_client.api_client import ApiClient
from istari_digital_client.openapi_client.models.user_state_option import (
    UserStateOption,
)
from istari_digital_client.models import User

if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client


class UsersApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_users_api = OpenApiUsersApi(api_client)
        self.client = client

    def list_users(
        self,
        user_state: UserStateOption | None = None,
    ) -> list[User]:
        openapi_users = self.openapi_users_api.list_users(
            user_state=user_state,
        )

        return [User(openapi_user) for openapi_user in openapi_users]

    def get_user_by_id(
        self,
        user_id: UUID | str,
    ) -> User:
        if isinstance(user_id, UUID):
            user_id = str(user_id)

        openapi_user = self.openapi_users_api.get_user_by_id(user_id)

        return User(openapi_user)
