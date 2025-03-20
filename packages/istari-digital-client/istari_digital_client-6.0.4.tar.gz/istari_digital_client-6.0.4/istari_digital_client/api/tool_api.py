import typing
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client.api.tools_api import (
    ToolsApi as OpenApiToolsApi,
)
from istari_digital_client.openapi_client.models import NewTool
from istari_digital_client.openapi_client.models import NewToolVersion
from istari_digital_client.openapi_client.models import UpdateTool
from istari_digital_client.openapi_client.api_client import ApiClient

from istari_digital_client.models import Tool
from istari_digital_client.models import ToolVersion
from istari_digital_client.models import ToolPage
from istari_digital_client.models import ToolVersionPage


if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client


class ToolApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_tools_api = OpenApiToolsApi(api_client)
        self.client: "Client" = client

    def add_tool(
        self,
        name: str,
        tool_versions: list[NewToolVersion] | None = None,
    ) -> Tool:
        new_tool = NewTool(
            name=name,
            tool_versions=tool_versions,
        )

        openapi_tool = self.openapi_tools_api.create_tool(
            new_tool=new_tool,
        )

        return Tool(openapi_tool, self.client)

    def add_tool_version(
        self,
        tool_id: UUID | str | Tool,
        new_tool_version: NewToolVersion,
    ) -> ToolVersion:
        if isinstance(tool_id, Tool):
            tool_id = str(tool_id.id)
        if isinstance(tool_id, UUID):
            tool_id = str(tool_id)

        openapi_tool_version = self.openapi_tools_api.create_tool_versions(
            tool_id=tool_id,
            new_tool_version=new_tool_version,
        )

        return ToolVersion(openapi_tool_version, self.client)

    def get_tool(
        self,
        tool_id: UUID | str | Tool,
    ) -> Tool:
        if isinstance(tool_id, Tool):
            tool_id = str(tool_id.id)
        if isinstance(tool_id, UUID):
            tool_id = str(tool_id)

        openapi_tool = self.openapi_tools_api.get_tool(
            tool_id=tool_id,
        )

        return Tool(openapi_tool, self.client)

    def get_tool_version(
        self,
        tool_version_id: UUID | str | ToolVersion,
    ) -> ToolVersion:
        if isinstance(tool_version_id, ToolVersion):
            tool_version_id = str(tool_version_id.id)
        if isinstance(tool_version_id, UUID):
            tool_version_id = str(tool_version_id)

        openapi_tool_version = self.openapi_tools_api.get_tool_version(
            tool_version_id=tool_version_id,
        )

        return ToolVersion(openapi_tool_version, self.client)

    def update_tool(
        self,
        tool_id: UUID | str | Tool,
        name: str,
    ) -> Tool:
        if isinstance(tool_id, Tool):
            tool_id = str(tool_id.id)
        if isinstance(tool_id, UUID):
            tool_id = str(tool_id)

        update_tool = UpdateTool(
            name=name,
        )

        openapi_tool = self.openapi_tools_api.update_tool(
            tool_id=tool_id,
            update_tool=update_tool,
        )

        return Tool(openapi_tool, self.client)

    def list_tools(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> ToolPage:
        openapi_tool_page = self.openapi_tools_api.list_tools(
            page=page,
            size=size,
            sort=sort,
        )

        return ToolPage(openapi_tool_page, self.client)

    def list_tool_versions(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> ToolVersionPage:
        openapi_tool_page = self.openapi_tools_api.list_tool_versions(
            page=page,
            size=size,
            sort=sort,
        )

        return ToolVersionPage(openapi_tool_page, self.client)
