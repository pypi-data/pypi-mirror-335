import typing
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client.api.agent_api import (
    AgentApi as OpenApiAgentApi,
)
from istari_digital_client.openapi_client.models import NewAgent
from istari_digital_client.openapi_client.models import NewAgentInformation
from istari_digital_client.openapi_client.models import NewAgentStatus
from istari_digital_client.openapi_client.models import NewAgentModuleVersion
from istari_digital_client.openapi_client.models import AgentStatusName
from istari_digital_client.openapi_client.api_client import ApiClient

from istari_digital_client.models import Agent
from istari_digital_client.models import AgentModules
from istari_digital_client.models import AgentPage
from istari_digital_client.models import AgentStatus
from istari_digital_client.models import AgentStatusPage

if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client


class AgentApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_agent_api = OpenApiAgentApi(api_client)
        self.client = client

    def _convert_agent_id(self, agent_id: UUID | str | Agent) -> str:
        if isinstance(agent_id, Agent):
            return str(agent_id.id)
        if isinstance(agent_id, UUID):
            return str(agent_id)
        return agent_id

    def register_agent(
        self,
        agent_identifier: str,
        agent_version: str,
        host_os: str,
    ) -> Agent:
        new_agent = NewAgent(
            agent_identifier=agent_identifier,
            agent_version=agent_version,
            host_os=host_os,
        )

        openapi_agent = self.openapi_agent_api.register_agent(new_agent=new_agent)
        return Agent(openapi_agent, self.client)

    def update_agent_information(
        self,
        agent_identifier: str | Agent,
        agent_version: str,
        host_os: str,
    ) -> Agent:
        if isinstance(agent_identifier, Agent):
            agent_identifier = agent_identifier.agent_identifier

        new_agent_information = NewAgentInformation(
            agent_version=agent_version,
            host_os=host_os,
        )

        openapi_agent = self.openapi_agent_api.update_agent_information(
            agent_identifier=agent_identifier,
            new_agent_information=new_agent_information,
        )
        return Agent(openapi_agent, self.client)

    def get_agent(
        self,
        agent_id: UUID | str | Agent,
    ) -> Agent:
        agent_id = self._convert_agent_id(agent_id)

        openapi_agent = self.openapi_agent_api.get_agent(agent_id=agent_id)
        return Agent(openapi_agent, self.client)

    def list_agents(
        self,
        agent_version: str | None = None,
        host_os: str | None = None,
        status_name: AgentStatusName | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> AgentPage:
        openapi_agent_page = self.openapi_agent_api.list_agents(
            agent_version=agent_version,
            host_os=host_os,
            status_name=status_name,
            page=page,
            size=size,
            sort=sort,
        )

        return AgentPage(openapi_agent_page, self.client)

    def update_agent_status(
        self,
        agent_identifier: str | Agent,
        agent_status: NewAgentStatus | AgentStatusName,
    ) -> Agent:
        if isinstance(agent_identifier, Agent):
            agent_identifier = agent_identifier.agent_identifier
        if isinstance(agent_status, AgentStatusName):
            agent_status = NewAgentStatus(name=agent_status)

        openapi_agent = self.openapi_agent_api.update_agent_status(
            agent_identifier=agent_identifier, new_agent_status=agent_status
        )
        return Agent(openapi_agent, self.client)

    def get_agent_status(
        self,
        agent_id: UUID | str | Agent,
    ) -> AgentStatus:
        agent_id = self._convert_agent_id(agent_id)

        openapi_agent_status = self.openapi_agent_api.get_agent_status(
            agent_id=agent_id
        )
        return AgentStatus(openapi_agent_status, self.client)

    def list_agent_status_history(
        self,
        agent_id: UUID | str | Agent,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> AgentStatusPage:
        agent_id = self._convert_agent_id(agent_id)

        openapi_agent_status_page = self.openapi_agent_api.list_agent_status_history(
            agent_id=agent_id,
            page=page,
            size=size,
            sort=sort,
        )

        return AgentStatusPage(openapi_agent_status_page, self.client)

    def update_agent_modules(
        self,
        agent_identifier: str | Agent,
        agent_modules: list[NewAgentModuleVersion],
    ) -> Agent:
        if isinstance(agent_identifier, Agent):
            agent_identifier = agent_identifier.agent_identifier

        openapi_agent = self.openapi_agent_api.update_agent_modules(
            agent_identifier=agent_identifier,
            new_agent_module_version=agent_modules,
        )
        return Agent(openapi_agent, self.client)

    def get_agent_modules(
        self,
        agent_id: UUID | str | Agent,
    ) -> AgentModules:
        agent_id = self._convert_agent_id(agent_id)

        openapi_agent_modules = self.openapi_agent_api.get_agent_modules(
            agent_id=agent_id
        )
        return AgentModules(openapi_agent_modules, self.client)
