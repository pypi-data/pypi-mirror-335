import typing
from uuid import UUID
from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client.api.operating_system_api import (
    OperatingSystemApi as OpenApiOperatingSystemApi,
)
from istari_digital_client.openapi_client.api_client import ApiClient

if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client

from istari_digital_client.openapi_client.models import NewOperatingSystem

from istari_digital_client.models import (
    OperatingSystem,
    OperatingSystemPage,
)


class OperatingSystemApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_operating_system_api = OpenApiOperatingSystemApi(api_client)
        self.client = client

    def create_operating_system(
        self,
        new_operating_system: NewOperatingSystem,
    ) -> OperatingSystem:
        openapi_operating_system = (
            self.openapi_operating_system_api.create_operating_system(
                new_operating_system=new_operating_system,
            )
        )

        return OperatingSystem(openapi_operating_system)

    def get_operating_system(
        self,
        operating_system_id: UUID | str | OperatingSystem,
    ) -> OperatingSystem:
        if isinstance(operating_system_id, OperatingSystem):
            operating_system_id = str(operating_system_id.id)
        if isinstance(operating_system_id, UUID):
            operating_system_id = str(operating_system_id)
        if isinstance(operating_system_id, str):
            operating_system_id = operating_system_id

        openapi_operating_system = (
            self.openapi_operating_system_api.get_operating_system(operating_system_id)
        )

        return OperatingSystem(openapi_operating_system)

    def list_operating_systems(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> OperatingSystemPage:
        openapi_page = self.openapi_operating_system_api.list_operating_systems(
            page=page,
            size=size,
            sort=sort,
        )

        return OperatingSystemPage(openapi_page)
