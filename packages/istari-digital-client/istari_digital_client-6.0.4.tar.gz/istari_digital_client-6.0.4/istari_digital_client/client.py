import logging
import shutil
from typing import Iterable
from uuid import UUID

from deprecation import deprecated  # type: ignore

from istari_digital_client.api.access_api import AccessApi
from istari_digital_client.api.agent_api import AgentApi
from istari_digital_client.api.artifact_api import ArtifactApi
from istari_digital_client.api.author_api import AuthorApi
from istari_digital_client.api.comment_api import CommentApi
from istari_digital_client.api.files_api import FilesApi
from istari_digital_client.api.job_api import JobApi
from istari_digital_client.api.model_api import ModelApi
from istari_digital_client.api.module_api import ModuleApi
from istari_digital_client.api.operating_system_api import OperatingSystemApi
from istari_digital_client.api.personal_access_token_api import PersonalAccessTokenApi
from istari_digital_client.api.revision_api import RevisionApi
from istari_digital_client.api.storage_api import StorageApi
from istari_digital_client.api.system_api import SystemApi
from istari_digital_client.api.tool_api import ToolApi
from istari_digital_client.api.users_api import UsersApi
from istari_digital_client.configuration import Configuration, ConfigurationError
from istari_digital_client.models import (
    AccessRelationship as AccessRelationship,
    FunctionSchema,
)
from istari_digital_client.models import Artifact, ArtifactPage
from istari_digital_client.models import Comment, CommentPage
from istari_digital_client.models import File, FilePage
from istari_digital_client.models import Function
from istari_digital_client.models import FunctionPage
from istari_digital_client.models import JSON as JSON
from istari_digital_client.models import Job, JobPage
from istari_digital_client.models import Model, ModelListItemPage
from istari_digital_client.models import PathLike as PathLike, NewSource
from istari_digital_client.models import ResourceLike
from istari_digital_client.models import Revision
from istari_digital_client.models import StatusName
from istari_digital_client.openapi_client.api_client import ApiClient
from istari_digital_client.openapi_client.models import NewToolVersion
from istari_digital_client.openapi_client.models import UpdateAccessRelationship
from istari_digital_client.openapi_client.models import UpdateSystem
from istari_digital_client.openapi_client.models import NewSnapshot
from istari_digital_client.openapi_client.models import NewSnapshotTag
from istari_digital_client.openapi_client.models import UpdateTag
from istari_digital_client.openapi_client.models import NewModuleManifest
from istari_digital_client.openapi_client.models import UserModelInputs
from istari_digital_client.openapi_client.models import NewAgentStatus
from istari_digital_client.openapi_client.models import NewAgentModuleVersion
from istari_digital_client.openapi_client.models import DeprecationReason
from istari_digital_client.openapi_client.models import System
from istari_digital_client.openapi_client.models import SystemBaseline
from istari_digital_client.openapi_client.models import SystemConfiguration
from istari_digital_client.openapi_client.models import PageSystem
from istari_digital_client.openapi_client.models import PageSystemConfiguration
from istari_digital_client.openapi_client.models import PageSnapshot
from istari_digital_client.openapi_client.models import PageSnapshotTag
from istari_digital_client.openapi_client.models import Snapshot
from istari_digital_client.openapi_client.models import ResponseCreateSnapshot
from istari_digital_client.openapi_client.models import SnapshotTag
from istari_digital_client.openapi_client.models import PageTrackedFile
from istari_digital_client.openapi_client.models import PageSnapshotItem
from istari_digital_client.openapi_client.models import NewSystem
from istari_digital_client.openapi_client.models import NewSystemConfiguration
from istari_digital_client.openapi_client.models import UsabilityStatusParams
from istari_digital_client.openapi_client.models import AccessResourceType
from istari_digital_client.openapi_client.models import AccessSubjectType
from istari_digital_client.models import Agent
from istari_digital_client.models import AgentModules
from istari_digital_client.models import AgentPage
from istari_digital_client.models import AgentStatus
from istari_digital_client.models import AgentStatusName
from istari_digital_client.models import AgentStatusPage
from istari_digital_client.models import ModuleAuthor
from istari_digital_client.models import ModuleAuthorPage
from istari_digital_client.models import OperatingSystem
from istari_digital_client.models import OperatingSystemPage
from istari_digital_client.models import Module
from istari_digital_client.models import ModuleVersion
from istari_digital_client.models import ModulePage
from istari_digital_client.models import ModuleVersionPage
from istari_digital_client.models import PersonalAccessToken
from istari_digital_client.models import PersonalAccessTokenPage
from istari_digital_client.models import Properties
from istari_digital_client.models import Token
from istari_digital_client.models import Tool
from istari_digital_client.models import ToolPage
from istari_digital_client.models import ToolVersion
from istari_digital_client.models import ToolVersionPage
from istari_digital_client.models import User
from istari_digital_client.models import AccessRelation
from istari_digital_client.openapi_client.models import PatchOp
from istari_digital_client.openapi_client.models import FilterBy
from istari_digital_client.openapi_client.models import ArchiveStatus
from istari_digital_client.openapi_client.models import NewOperatingSystem
from istari_digital_client.openapi_client.models import UserStateOption

logger = logging.getLogger("istari-digital-client.client")


class Client:
    """Create a new instance of the Istari client

    Args:
        config (Configuration | None): The configuration for the client

    Returns:
        Client: The Istari client instance
    """

    access: AccessApi
    agent: AgentApi
    model: ModelApi
    artifact: ArtifactApi
    comment: CommentApi
    file: FilesApi
    revision: RevisionApi
    storage: StorageApi
    system: SystemApi
    user: UsersApi
    personal_access_token: PersonalAccessTokenApi
    job: JobApi
    module: ModuleApi
    operating_system: OperatingSystemApi
    author: AuthorApi
    tool: ToolApi

    def __init__(
        self: "Client",
        config: Configuration | None = None,
    ) -> None:
        config = config or Configuration()

        if not config.registry_url:
            raise ConfigurationError(
                "Registry URL not set! Must be specified, either via ISTART_REGISTRY_URL env or by explicitly setting "
                "in  'registry_url' parameter in (optional) configuration parameter on client initialization"
            )
        if not config.registry_auth_token:
            logger.warning("registry auth token not set!")

        self.configuration: Configuration = config

        self._api_client = ApiClient(config.openapi_client_configuration)

        self.access = AccessApi(config, self)
        self.agent = AgentApi(config, self)
        self.model = ModelApi(config, self)
        self.artifact = ArtifactApi(config, self)
        self.comment = CommentApi(config, self)
        self.file = FilesApi(config, self)
        self.revision = RevisionApi(config, self)
        self.storage = StorageApi(config, self)
        self.system = SystemApi(config, self)
        self.user = UsersApi(config, self)
        self.personal_access_token = PersonalAccessTokenApi(config, self)
        self.job = JobApi(config, self)
        self.module = ModuleApi(config, self)
        self.operating_system = OperatingSystemApi(config, self)
        self.author = AuthorApi(config, self)
        self.tool = ToolApi(config, self)

    def __del__(self):
        if (
            self.configuration.filesystem_cache_enabled
            and self.configuration.filesystem_cache_clean_on_exit
            and self.configuration.filesystem_cache_root.exists()
            and self.configuration.filesystem_cache_root.is_dir()
        ):
            logger.debug("Cleaning up cache contents for client exit")
            for child in self.configuration.filesystem_cache_root.iterdir():
                if child.is_dir():
                    logger.debug("deleting cache directory - %s", child)
                    shutil.rmtree(
                        self.configuration.filesystem_cache_root, ignore_errors=True
                    )
                elif child.is_file() and not child.is_symlink():
                    logger.debug("deleting cache file - %s", child)
                    child.unlink(missing_ok=True)
                else:
                    logger.debug(
                        "not deleting cache item (is neither a directory nor a regular file) -  %s",
                        child,
                    )

    def get_resource(
        self, resource_type: type[ResourceLike], resource_id: UUID
    ) -> ResourceLike:
        """Get a resource

        Args:
            resource_type (type[ResourceLike]): The type of the resource
            resource_id (UUID): The ID of the resource

        Returns:
            ResourceLike: The resource with the given ID

        """
        if resource_type == Artifact:
            return self.get_artifact(resource_id)
        elif resource_type == Comment:
            return self.get_comment(resource_id)
        elif resource_type == Model:
            return self.get_model(resource_id)
        elif resource_type == Job:
            return self.get_job(resource_id)
        else:
            raise TypeError(
                f"Unsupported resource type for get_resource(): {resource_type}"
            )

    @deprecated(
        deprecated_in="4.1.0",
        current_version="4.1.0",
        details="This method is deprecated, please use list_access instead",
    )
    def list_artifact_access(
        self,
        artifact_id: str | UUID | Artifact,
    ) -> list[AccessRelationship]:
        """List access for an artifact

        Args:
            artifact_id (str | UUID | Artifact): The artifact to list access for

        Returns:
            list[AccessRelationship]: List of access relationships for the artifact

        """
        return self.access.list_artifact_access(artifact_id)

    @deprecated(
        deprecated_in="4.1.0",
        current_version="4.1.0",
        details="This method is deprecated, please use list_access instead",
    )
    def list_job_access(
        self,
        job_id: str | UUID | Job,
    ) -> list[AccessRelationship]:
        """List access for a job

        Args:
            job_id (str | UUID | Job): The job to list access for

        Returns:
            list[AccessRelationship]: List of access relationships for the job

        """
        return self.access.list_job_access(job_id)

    @deprecated(
        deprecated_in="4.1.0",
        current_version="4.1.0",
        details="This method is deprecated, please use list_access instead",
    )
    def list_model_access(
        self,
        model_id: UUID | str | Model,
    ) -> list[AccessRelationship]:
        """List access for a model

        Args:
            model_id (str | UUID | Model): The model to list access for

        Returns:
            list[AccessRelationship]: List of access relationships for the model

        """
        return self.access.list_model_access(model_id)

    @deprecated(
        deprecated_in="4.1.0",
        current_version="4.1.0",
        details="This method is deprecated, please use list_access instead",
    )
    def list_function_access(
        self,
        function_id: str | UUID | Function,
    ) -> list[AccessRelationship]:
        """List access for a function

        Args:
            function_id (str | UUID | Function): The function to list access for

        Returns:
            list[AccessRelationship]: List of access relationships for the function

        """
        return self.access.list_function_access(function_id)

    @deprecated(
        deprecated_in="4.1.0",
        current_version="4.1.0",
        details="This method is deprecated, please use update_access instead",
    )
    def patch_artifact_access(
        self,
        artifact_id: str | UUID | Artifact,
        relationship: AccessRelationship,
        patch_op: PatchOp | None = None,
    ) -> list[AccessRelationship]:
        """Patch access for an artifact

        Args:
            artifact_id (str | UUID | Artifact): The artifact to patch access for
            relationship (AccessRelationship): The access relationship to patch
            patch_op (PatchOp | None): The patch operation to apply

        Returns:
            list[AccessRelationship]: List of access relationships for the artifact after patching

        """
        return self.access.patch_artifact_access(artifact_id, relationship, patch_op)

    @deprecated(
        deprecated_in="4.1.0",
        current_version="4.1.0",
        details="This method is deprecated, please use update_access instead",
    )
    def patch_job_access(
        self,
        job_id: str | UUID | Job,
        relationship: AccessRelationship,
        patch_op: PatchOp | None = None,
    ) -> list[AccessRelationship]:
        """Patch access for a job

        Args:
            job_id (str | UUID | Job): The job to patch access for
            relationship (AccessRelationship): The access relationship to patch
            patch_op (PatchOp | None): The patch operation to apply

        Returns:
            list[AccessRelationship]: List of access relationships for the job after patching

        """
        return self.access.patch_job_access(job_id, relationship, patch_op)

    @deprecated(
        deprecated_in="4.1.0",
        current_version="4.1.0",
        details="This method is deprecated, please use update_access instead",
    )
    def patch_model_access(
        self,
        model_id: UUID | str | Model,
        relationship: AccessRelationship,
        patch_op: PatchOp | None = None,
    ) -> list[AccessRelationship]:
        """Patch access for a model

        Args:
            model_id (str | UUID | Model): The model to patch access for
            relationship (AccessRelationship): The access relationship to patch
            patch_op (PatchOp | None): The patch operation to apply

        Returns:
            list[AccessRelationship]: List of access relationships for the model after patching

        """
        return self.access.patch_model_access(model_id, relationship, patch_op)

    @deprecated(
        deprecated_in="4.1.0",
        current_version="4.1.0",
        details="This method is deprecated, please use update_access instead",
    )
    def patch_function_access(
        self,
        function_id: str | UUID | Function,
        relationship: AccessRelationship,
        patch_op: PatchOp | None = None,
    ) -> list[AccessRelationship]:
        """Patch access for a function

        Args:
            function_id (str | UUID | Function): The function to patch access for
            relationship (AccessRelationship): The access relationship to patch
            patch_op (PatchOp | None): The patch operation to apply

        Returns:
            list[AccessRelationship]: List of access relationships for the function after patching

        """
        return self.access.patch_function_access(function_id, relationship, patch_op)

    def register_agent(
        self,
        agent_identifier: str,
        agent_version: str,
        host_os: str,
    ) -> Agent:
        """Register an agent

        Args:
            agent_identifier (str): The identifier for the agent
            agent_version (str): The version of the agent
            host_os (str): The OS of the VM hosting the agent

        Returns:
            Agent: The registered agent

        """
        return self.agent.register_agent(agent_identifier, agent_version, host_os)

    def update_agent_information(
        self,
        agent_identifier: str | Agent,
        agent_version: str,
        host_os: str,
    ) -> Agent:
        """Update an agent's information

        Args:
            agent_identifier (str | Agent): The identifier for the agent to update
            agent_version (str): The updated version of the agent
            host_os (str): The updated OS of the VM hosting the agent

        Returns:
            Agent: The updated agent

        """
        return self.agent.update_agent_information(
            agent_identifier, agent_version, host_os
        )

    def get_agent(self, agent_id: UUID | str | Agent) -> Agent:
        """Get an agent

        Args:
            agent_id (str | UUID | Agent): The agent to get

        Returns:
            Agent: The agent with the given ID

        """
        return self.agent.get_agent(agent_id=agent_id)

    def list_agents(
        self,
        agent_version: str | None = None,
        host_os: str | None = None,
        status_name: AgentStatusName | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> AgentPage:
        """List agents

        Args:
            agent_version (str | None): The agent version to filter on
            host_os (str | None): The agent host OS to filter on
            status_name (AgentStatusName | None): The agent status to filter on
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            AgentPage: Page of agents

        """
        return self.agent.list_agents(
            agent_version, host_os, status_name, page, size, sort
        )

    def update_agent_status(
        self,
        agent_identifier: str | Agent,
        agent_status: NewAgentStatus | AgentStatusName,
    ) -> Agent:
        """Update an agent's status

        Args:
            agent_identifier (str | Agent): The identifier for the agent to update
            agent_status (NewAgentStatus | AgentStatusName): The status of the agent

        Returns:
            Agent: The updated agent

        """
        return self.agent.update_agent_status(agent_identifier, agent_status)

    def get_agent_status(self, agent_id: UUID | str | Agent) -> AgentStatus:
        """Get an agent's status

        Args:
            agent_id (str | UUID | Agent): The agent to get the status of

        Returns:
            AgentStatus: The status of the agent with the given ID

        """
        return self.agent.get_agent_status(agent_id)

    def list_agent_status_history(
        self,
        agent_id: UUID | str | Agent,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> AgentStatusPage:
        """List agent's status history

        Args:
            agent_id (UUID | str | Agent): The id of the agent to get the status history of
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            AgentStatusPage: Page of agent's statuses

        """
        return self.agent.list_agent_status_history(agent_id, page, size, sort)

    def update_agent_modules(
        self,
        agent_identifier: str | Agent,
        agent_modules: list[NewAgentModuleVersion],
    ) -> Agent:
        """Update an agent's modules

        Args:
            agent_identifier (str | Agent): The identifier for the agent to update
            agent_modules (list[NewAgentModules]): The modules of the agent

        Returns:
            Agent: The updated agent

        """
        return self.agent.update_agent_modules(agent_identifier, agent_modules)

    def get_agent_modules(self, agent_id: UUID | str | Agent) -> AgentModules:
        """Get an agent's modules

        Args:
            agent_id (str | UUID | Agent): The agent to get the modules of

        Returns:
            AgentModules: The modules of the agent with the given ID

        """
        return self.agent.get_agent_modules(agent_id)

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
    ) -> "Artifact":
        """Add an artifact

        Args:
            model_id (Model | str | UUID): The model to add the artifact to
            path (PathLike): The path to the artifact
            sources (Iterable[ResourceLike | File | Revision | UUID | str] | None): The sources of the artifact
            description (str | None): The description of the artifact
            version_name (str | None): The version name of the artifact
            external_identifier (str | None): The external identifier of the artifact
            display_name (str | None): The display name of the artifact

        Returns:
            Artifact: The added artifact

        """
        return self.artifact.add_artifact(
            model_id,
            path,
            sources,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
            display_name=display_name,
        )

    def get_artifact(self, artifact_id: str | UUID) -> "Artifact":
        """Get an artifact

        Args:
            artifact_id (str | UUID): The artifact to get

        Returns:
            Artifact: The artifact with the given ID

        """
        return self.artifact.get_artifact(artifact_id)

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
    ) -> "Artifact":
        """Update an artifact

        Args:
            artifact_id (Artifact | UUID | str): The artifact to update
            path (PathLike): The path to the artifact
            sources (Iterable[ResourceLike | File | Revision | UUID | str] | None): The sources of the artifact
            description (str | None): The description of the artifact
            version_name (str | None): The version name of the artifact
            external_identifier (str | None): The external identifier of the artifact
            display_name (str | None): The display name of the artifact

        Returns:
            Artifact: The updated artifact

        """
        return self.artifact.update_artifact(
            artifact_id,
            path,
            sources,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
            display_name=display_name,
        )

    def list_artifacts(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        created_by: str | FilterBy | None = None,
    ) -> ArtifactPage:
        """List artifacts

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order
            created_by (str | FilterBy | None): Filter by created by or shared with user

        Returns:
            ArtifactPage: Page of artifacts

        """
        return self.artifact.list_artifacts(
            page=page,
            size=size,
            sort=sort,
            created_by=created_by,
        )

    def list_artifact_comments(
        self,
        artifact_id: str | UUID | Artifact,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> CommentPage:
        """List comments for an artifact

        Args:
            artifact_id (str | UUID | Artifact): The artifact to list comments for
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            CommentPage: Page of comments for the artifact

        """
        return self.artifact.list_artifact_comments(
            artifact_id,
            page=page,
            size=size,
            sort=sort,
        )

    def add_comment(
        self,
        resource_id: str | UUID | ResourceLike,
        path: PathLike,
        description: str | None = None,
    ) -> "Comment":
        """Add a comment to a resource

        Args:
            resource_id (str | UUID | ResourceLike): The resource to add the comment to
            path (PathLike): The path to the comment
            description (str | None): The description of the comment

        Returns:
            Comment: The added comment

        """
        return self.comment.add_comment(resource_id, path, description)

    def get_comment(self, comment_id: str | UUID | Comment) -> "Comment":
        """Get a comment

        Args:
            comment_id (str | UUID | Comment): The comment to get

        Returns:
            Comment: The comment with the given ID

        """
        return self.comment.get_comment(comment_id)

    def update_comment(
        self,
        comment_id: str | UUID | Comment,
        path: PathLike,
        description: str | None = None,
    ) -> "Comment":
        """Update a comment

        Args:
            comment_id (str | UUID | Comment): The comment to update
            path (PathLike): The path to the comment
            description (str | None): The description of the comment

        Returns:
            Comment: The updated comment

        """
        return self.comment.update_comment(comment_id, path, description)

    def add_file(
        self,
        path: PathLike,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> "File":
        """Add a file

        Args:
            path (PathLike): The path to the file
            sources (Iterable[ResourceLike | File | Revision | UUID | str] | None): The sources of the file
            description (str | None): The description of the file
            version_name (str | None): The version name of the file
            external_identifier (str | None): The external identifier of the file
            display_name (str | None): The display name of the file

        Returns:
            File: The added file

        """
        return self.file.add_file(
            path,
            sources,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
            display_name=display_name,
        )

    def get_file(self, file_id: str | UUID | File) -> "File":
        """Get a file

        Args:
            file_id (str | UUID): The file to get

        Returns:
            File: The file with the given ID

        """
        return self.file.get_file(file_id)

    def get_file_by_revision_id(self, revision_id: str | UUID) -> "File":
        """Get a file by revision ID

        Args:
            revision_id (str | UUID): The revision ID of the file to get

        Returns:
            File: The file with the given revision ID

        """
        return self.file.get_file_by_revision_id(revision_id)

    def list_files(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        created_by: str | FilterBy | None = None,
    ) -> "FilePage":
        """List files

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order
            created_by (str | FilterBy | None): Filter by created by or shared with user

        Returns:
            FilePage: Page of files

        """
        return self.file.list_files(
            page=page,
            size=size,
            sort=sort,
            created_by=created_by,
        )

    def update_file(
        self,
        file_id: File | UUID | str,
        path: PathLike | str,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> "File":
        """Update a file

        Args:
            file_id (File | UUID | str): The file to update
            path (PathLike): The path to the file
            sources (Iterable[ResourceLike | File | Revision | UUID | str] | None): The sources of the file
            description (str | None): The description of the file
            version_name (str | None): The version name of the file
            external_identifier (str | None): The external identifier of the file
            display_name (str | None): The display name of the file

        Returns:
            File: The updated file

        """
        return self.file.update_file(
            file_id,
            path,
            sources,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
            display_name=display_name,
        )

    def update_file_properties(
        self,
        file: "File",
        display_name: str | None = None,
        description: str | None = None,
    ) -> "File":
        """Update file properties

        Args:
            file (File): The file to update
            display_name (str | None): The display name of the file
            description (str | None): The description of the file

        Returns:
            File: The updated file

        """
        return self.file.update_file_properties(
            file,
            display_name=display_name,
            description=description,
        )

    def add_job(
        self,
        model_id: UUID | str | Model,
        function: str,
        *,
        parameters: JSON | None = None,
        parameters_file: PathLike | None = None,
        tool_name: str | None = None,
        tool_version: str | None = None,
        operating_system: str | None = None,
        agent_identifier: str | None = None,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
        **kwargs,
    ) -> "Job":
        """Add a job

        Args:
            model_id (Model | UUID | str): The model to add the job to
            function (str): The function of the job
            parameters (JSON | None): The parameters of the job
            parameters_file (PathLike | None): The path to the parameters file
            tool_name (str | None): The name of the tool
            tool_version (str | None): The version of the tool
            operating_system (str | None): The operating system of the agent
            agent_identifier (str | None): The identifier of the agent
            sources (Iterable[ResourceLike | File | Revision | UUID | str] | None): The sources of the job
            description (str | None): The description of the job
            version_name (str | None): The version name of the job
            external_identifier (str | None): The external identifier of the job
            display_name (str | None): The display name of the job

        Returns:
            Job: The added job

        """
        return self.job.add_job(
            model_id,
            function,
            parameters=parameters,
            parameters_file=parameters_file,
            tool_name=tool_name,
            tool_version=tool_version,
            operating_system=operating_system,
            agent_identifier=agent_identifier,
            sources=sources,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
            display_name=display_name,
            **kwargs,
        )

    def get_job(self, job_id: UUID | str | Job) -> "Job":
        """Get a job

        Args:
            job_id (str | UUID): The job to get

        Returns:
            Job: The job with the given ID

        """
        return self.job.get_job(job_id)

    def list_jobs(
        self,
        model_id: UUID | str | Model | None = None,
        status_name: StatusName | None = None,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> "JobPage":
        """List jobs

        Args:
            model_id (UUID | str | Model | None): The model ID to filter by
            status_name (StatusName | None): The status name to filter by
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            JobPage: Page of jobs

        """
        return self.job.list_jobs(
            model_id=model_id,
            status_name=status_name,
            page=page,
            size=size,
            sort=sort,
        )

    def update_job(
        self,
        job_id: UUID | str | Job,
        path: PathLike,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> "Job":
        """Update a job

        Args:
            job_id (UUID | str | Job): The job to update
            path (PathLike): The path to the job
            sources (Iterable[ResourceLike | File | Revision | UUID | str] | None): The sources of the job
            description (str | None): The description of the job
            version_name (str | None): The version name of the job
            external_identifier (str | None): The external identifier of the job
            display_name (str | None): The display name of the job

        Returns:
            Job: The updated job

        """
        return self.job.update_job(
            job_id,
            path,
            sources,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
            display_name=display_name,
        )

    def update_job_status(
        self,
        job_id: UUID | str | Job,
        status_name: StatusName,
        agent_identifier: str | None = None,
    ) -> "Job":
        """Update job status

        Args:
            job_id (UUID | str | Job): The job to update
            status_name (StatusName): The status name to set
            agent_identifier (str | None): The identifier of the agent

        Returns:
            Job: The updated job

        """
        return self.job.update_job_status(job_id, status_name, agent_identifier)

    def add_model(
        self,
        path: PathLike,
        sources: Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
        | None = None,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> "Model":
        """Add a model

        Args:
            path (PathLike): The path to the model
            sources (Iterable[ResourceLike | File | Revision | UUID | str] | None): The sources of the model
            description (str | None): The description of the model
            version_name (str | None): The version name of the model
            external_identifier (str | None): The external identifier of the model
            display_name (str | None): The display name of the model

        Returns:
            Model: The added model

        """
        return self.model.add_model(
            path,
            sources,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
            display_name=display_name,
        )

    def update_model(
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
    ) -> "Model":
        """Update a model

        Args:
            model_id (Model | UUID | str): The model to update
            path (PathLike): The path to the model
            sources (Iterable[ResourceLike | File | Revision | UUID | str] | None): The sources of the model
            description (str | None): The description of the model
            version_name (str | None): The version name of the model
            external_identifier (str | None): The external identifier of the model
            display_name (str | None): The display name of the model

        Returns:
            Model: The updated model

        """
        return self.model.update_model(
            model_id,
            path,
            sources,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
            display_name=display_name,
        )

    def get_model(self, model_id: UUID | str | Model) -> "Model":
        """Get a model

        Args:
            model_id (Model | str | UUID): The model to get

        Returns:
            Model: The model with the given ID

        """
        return self.model.get_model(model_id)

    def list_models(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        created_by: str | FilterBy | None = None,
        archive_status: str | ArchiveStatus | None = None,
    ) -> ModelListItemPage:
        """List models

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order
            created_by (str | FilterBy | None): Filter by created by or shared with user
            archive_status (str | ArchiveStatus | None): Filter by archive status

        Returns:
            ModelListItemPage: Page of models

        """
        return self.model.list_models(
            page=page,
            size=size,
            sort=sort,
            created_by=created_by,
            archive_status=archive_status,
        )

    def list_model_artifacts(
        self,
        model_id: UUID | str | Model,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        created_by: str | FilterBy | None = None,
        archive_status: str | ArchiveStatus | None = None,
    ) -> "ArtifactPage":
        """List model artifacts

        Args:
            model_id (Model | str | UUID): The model to list artifacts for
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order
            created_by (str | FilterBy | None): Filter by created by or shared with user
            archive_status (str | ArchiveStatus | None): Filter by archive status

        Returns:
            ArtifactPage: Page of artifacts for the model

        """
        return self.model.list_model_artifacts(
            model_id,
            page=page,
            size=size,
            sort=sort,
            created_by=created_by,
            archive_status=archive_status,
        )

    def list_model_comments(
        self,
        model_id: UUID | str | Model,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        archive_status: str | ArchiveStatus | None = None,
    ) -> CommentPage:
        """List comments for a model

        Args:
            model_id (Model | str | UUID): The model to list comments for
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order
            archive_status (str | ArchiveStatus | None): Filter by archive status

        Returns:
            CommentPage: Page of comments for the model

        """
        return self.model.list_model_comments(
            model_id,
            page=page,
            size=size,
            sort=sort,
            archive_status=archive_status,
        )

    def list_model_jobs(
        self,
        model_id: UUID | str | Model,
        status_name: StatusName | None = None,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        archive_status: str | ArchiveStatus | None = None,
    ) -> JobPage:
        """List jobs for a model

        Args:
            model_id (Model | str | UUID): The model to list jobs for
            status_name (StatusName | None): The status name to filter by
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order
            archive_status (str | ArchiveStatus | None): Filter by archive status

        Returns:
            JobPage: Page of jobs for the model

        """
        return self.model.list_model_jobs(
            model_id,
            status_name=status_name,
            page=page,
            size=size,
            sort=sort,
            archive_status=archive_status,
        )

    def create_module(
        self,
        new_module_manifest: NewModuleManifest,
    ) -> "Module":
        """Create a module

        Args:
            new_module_manifest (NewModuleManifest): The module manifest to add

        Returns:
            Module: The created module

        """
        return self.module.create_module(new_module_manifest)

    def create_operating_system(
        self,
        new_operating_system: NewOperatingSystem,
    ) -> "OperatingSystem":
        """Create an operating system

        Args:
            new_operating_system (NewOperatingSystem): The operating system to add

        Returns:
            OperatingSystem: The added operating system

        """
        return self.operating_system.create_operating_system(new_operating_system)

    def get_function(self, function_id: UUID | str | Function) -> "Function":
        """Get a function

        Args:
            function_id (UUID | str | Function): The function to get

        Returns:
            Function: The function with the given ID

        """
        return self.module.get_function(function_id)

    def get_module(self, module_id: UUID | str | Module) -> "Module":
        """Get a module

        Args:
            module_id (UUID | str | Module): The module to get

        Returns:
            Module: The module with the given ID

        """
        return self.module.get_module(module_id)

    def get_module_version(
        self,
        module_version_id: UUID | str | ModuleVersion,
    ) -> "ModuleVersion":
        """Get a module version

        Args:
            module_version_id (UUID | str | ModuleVersion): The module version to get

        Returns:
            ModuleVersion: The module version with the given ID

        """
        return self.module.get_module_version(module_version_id)

    def get_operating_system(
        self,
        operating_system_id: UUID | str | OperatingSystem,
    ) -> "OperatingSystem":
        """Get an operating system

        Args:
            operating_system_id (UUID | str | OperatingSystem): The operating system to get

        Returns:
            OperatingSystem: The operating system with the given ID

        """
        return self.operating_system.get_operating_system(operating_system_id)

    def list_functions(
        self,
        *,
        name: str | None = None,
        module_version: str | None = None,
        tool: str | None = None,
        tool_version: str | None = None,
        operating_system: str | None = None,
        input_extension: str | None = None,
        input_user_models: UserModelInputs | None = None,
        status: UsabilityStatusParams | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> "FunctionPage":
        """List functions

        Args:
            name (str | None): None,
            module_version (str | None): None,
            tool (str | None): None,
            tool_version (str | None): None,
            operating_system (str | None): None,
            input_extension (str | None): None,
            input_user_models ("single" | "multiple" | None): None,
            status (UsabilityStatusParams | None): None,
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            FunctionPage: Page of functions

        """
        return self.module.list_functions(
            name=name,
            module_version=module_version,
            tool=tool,
            tool_version=tool_version,
            operating_system=operating_system,
            input_extension=input_extension,
            input_user_models=input_user_models,
            status=status,
            page=page,
            size=size,
            sort=sort,
        )

    def get_function_schema(self, *, function_schema_id: str) -> FunctionSchema:
        """Get function schema

        Args:
            function_schema_id (str): the id of the function schema

        Returns:
            FunctionSchema: Function Schema

        """
        return self.module.get_function_schema(function_schema_id=function_schema_id)

    def list_modules(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> "ModulePage":
        """List modules

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            ModulePage: Page of modules

        """
        return self.module.list_modules(
            page=page,
            size=size,
            sort=sort,
        )

    def list_module_versions(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> "ModuleVersionPage":
        """List module versions

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            ModuleVersionPage: Page of module versions

        """
        return self.module.list_module_versions(
            page=page,
            size=size,
            sort=sort,
        )

    def list_operating_systems(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> "OperatingSystemPage":
        """List operating systems

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            OperatingSystemPage: Page of operating systems

        """
        return self.operating_system.list_operating_systems(
            page=page,
            size=size,
            sort=sort,
        )

    def add_author(
        self,
        name: str,
        email: str,
    ) -> ModuleAuthor:
        """Add an author

        Args:
            name (str): The name of the author
            email (str): The email of the author

        Returns:
            ModuleAuthor: The added author

        """
        return self.author.add_author(name, email)

    def update_author(
        self,
        author_id: UUID | str | ModuleAuthor,
        name: str,
        email: str,
    ) -> ModuleAuthor:
        """Update an author

        Args:
            author_id (UUID | str | ModuleAuthor): The author to update
            name (str): The name of the author
            email (str): The email of the author

        Returns:
            ModuleAuthor: The updated author

        """
        return self.author.update_author(author_id, name, email)

    def get_author(
        self,
        author_id: UUID | str | ModuleAuthor,
    ) -> ModuleAuthor:
        """Get an author

        Args:
            author_id (UUID | str | ModuleAuthor): The author to get

        Returns:
            ModuleAuthor: The author with the given ID

        """
        return self.author.get_author(author_id)

    def list_authors(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> ModuleAuthorPage:
        """List authors

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            ModuleAuthorPage: Page of authors

        """
        return self.author.list_authors(
            page=page,
            size=size,
            sort=sort,
        )

    def add_tool(
        self,
        name: str,
        tool_versions: list[NewToolVersion] | None = None,
    ) -> Tool:
        """Add a tool

        Args:
            name (str): The name of the tool
            tool_versions (list[NewToolVersion] | None): The tool versions of the tool

        Returns:
            Tool: The added tool

        """
        return self.tool.add_tool(
            name,
            tool_versions=tool_versions,
        )

    def add_tool_version(
        self,
        tool_id: Tool | UUID | str,
        new_tool_version: NewToolVersion,
    ) -> ToolVersion:
        """Add a tool version

        Args:
            tool_id (Tool | UUID | str): The tool to add the tool version to
            new_tool_version (NewToolVersion): The tool version to add

        Returns:
            ToolVersion: The added tool version

        """
        return self.tool.add_tool_version(tool_id, new_tool_version)

    def get_tool(
        self,
        tool_id: Tool | UUID | str,
    ) -> Tool:
        """Get a tool

        Args:
            tool_id (Tool | UUID | str): The tool to get

        Returns:
            Tool: The tool with the given ID

        """
        return self.tool.get_tool(tool_id)

    def get_tool_version(
        self,
        tool_version_id: ToolVersion | UUID | str,
    ) -> ToolVersion:
        """Get a tool version

        Args:
            tool_version_id (ToolVersion | UUID | str): The tool version to get

        Returns:
            ToolVersion: The tool version with the given ID

        """
        return self.tool.get_tool_version(tool_version_id)

    def update_tool(
        self,
        tool_id: Tool | UUID | str,
        name: str,
    ) -> Tool:
        """Update a tool

        Args:
            tool_id (Tool | UUID | str): The tool to update
            name (str): The updated name of the tool

        Returns:
            Tool: The updated tool

        """
        return self.tool.update_tool(tool_id, name)

    def list_tools(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> ToolPage:
        """List tools

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            ToolPage: Page of tools

        """
        return self.tool.list_tools(
            page=page,
            size=size,
            sort=sort,
        )

    def list_tool_versions(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> ToolVersionPage:
        """List tool versions

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            ToolVersionPage: Page of tool versions

        """
        return self.tool.list_tool_versions(
            page=page,
            size=size,
            sort=sort,
        )

    def deprecate_module(
        self,
        module_id: UUID | str | Module,
        reason: DeprecationReason,
    ) -> Module:
        """Deprecate a module

        Args:
            module_id (UUID | str | Module): The module to update
            reason (DeprecationReason): The reason to set

        Returns:
            Module: The deprecated module

        """
        return self.module.deprecate_module(module_id, reason)

    def deprecate_module_version(
        self,
        module_version_id: UUID | str | ModuleVersion,
        reason: DeprecationReason,
    ) -> ModuleVersion:
        """Deprecate module version

        Args:
            module_version_id (UUID | str | ModuleVersion): The module version to deprecate
            reason (DeprecationReason): The reason to set

        Returns:
            ModuleVersion: The deprecated module version

        """
        return self.module.deprecate_module_version(module_version_id, reason)

    def create_agent_personal_access_token(
        self,
        name: str,
    ) -> "PersonalAccessToken":
        """Add an agent personal access token

        Args:
            name (str): The name of the personal access token

        Returns:
            PersonalAccessToken: The added personal access token

        """
        return self.personal_access_token.create_agent_personal_access_token(name)

    def create_personal_access_token(
        self,
        name: str,
    ) -> "PersonalAccessToken":
        """Add a personal access token

        Args:
            name (str): The name of the personal access token

        Returns:
            PersonalAccessToken: The added personal access token

        """
        return self.personal_access_token.create_personal_access_token(name)

    def delete_personal_access_token(
        self,
        pat_id: PersonalAccessToken | UUID | str,
    ) -> None:
        """Delete a personal access token

        Args:
            pat_id (PersonalAccessToken | UUID | str): The personal access token to delete

        Returns:
            None

        """
        return self.personal_access_token.delete_personal_access_token(pat_id)

    def list_personal_access_tokens(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> "PersonalAccessTokenPage":
        """List personal access tokens

        Args:
            page (int | None): The page number
            size (int | None): The page size
            sort (str | None): The sort order

        Returns:
            PersonalAccessTokenPage: Page of personal access tokens

        """
        return self.personal_access_token.list_personal_access_tokens(
            page=page,
            size=size,
            sort=sort,
        )

    def revoke_all_personal_access_tokens(self) -> None:
        """Revoke all personal access tokens

        Args:
            None

        Returns:
            None

        """
        return self.personal_access_token.revoke_all_personal_access_tokens()

    def get_revision(self, revision_id: str | UUID) -> "Revision":
        """Get a revision

        Args:
            revision_id (UUID | str): The revision to get

        Returns:
            Revision: The revision with the given ID

        """
        return self.revision.get_revision(revision_id)

    def read_contents(self, token: Token) -> bytes:
        """Read contents of a revision

        Args:
            token (Token): The content token of the revision

        Returns:
            bytes: The contents of the revision

        """
        return self.storage.read_contents(token.inner)

    def read_properties(self, token: Token) -> Properties:
        """Read properties of a revision

        Args:
            token (Token): The properties token of the revision

        Returns:
            Properties: The properties of the revision

        """
        return self.storage.read_properties(token.inner)

    def list_users(
        self,
        user_state: UserStateOption | None = None,
    ) -> list[User]:
        """List users

        Args:
            user_state (UserStateOption | None): The user state to filter by

        Returns:
            list[User]: List of users

        """
        return self.user.list_users(user_state)

    def get_user_by_id(
        self,
        user_id: UUID | str,
    ) -> User:
        """Get a user by ID

        Args:
            user_id (UUID | str): The user ID

        Returns:
            User: The user with the given ID
        """
        return self.user.get_user_by_id(user_id)

    def archive_model(
        self, model_id: UUID | str | Model, reason: str | None = None
    ) -> Model:
        return self.model.archive_model(model_id, reason)

    def restore_model(
        self, model_id: UUID | str | Model, reason: str | None = None
    ) -> Model:
        return self.model.restore_model(model_id, reason)

    def archive_comment(
        self, comment_id: UUID | str | Comment, reason: str | None = None
    ) -> Comment:
        return self.comment.archive_comment(comment_id, reason)

    def restore_comment(
        self, comment_id: UUID | str | Comment, reason: str | None = None
    ) -> Comment:
        return self.comment.restore_comment(comment_id, reason)

    def archive_artifact(
        self, artifact_id: UUID | str | Artifact, reason: str | None = None
    ) -> Artifact:
        return self.artifact.archive_artifact(artifact_id, reason)

    def restore_artifact(
        self, artifact_id: UUID | str | Artifact, reason: str | None = None
    ) -> Artifact:
        return self.artifact.restore_artifact(artifact_id, reason)

    def archive_file(
        self, file_id: UUID | str | File, reason: str | None = None
    ) -> File:
        return self.file.archive_file(file_id, reason)

    def restore_file(
        self, file_id: UUID | str | File, reason: str | None = None
    ) -> File:
        return self.file.restore_file(file_id, reason)

    def archive_revision(
        self, revision_id: UUID | str | Revision, reason: str | None = None
    ) -> Revision:
        return self.revision.archive_revision(revision_id, reason)

    def restore_revision(
        self, revision_id: UUID | str | Revision, reason: str | None = None
    ) -> Revision:
        return self.revision.restore_revision(revision_id, reason)

    def copy_revision_to_new_file(self, revision_id: str | UUID | Revision) -> File:
        return self.revision.copy_revision_to_new_file(revision_id)

    def copy_revision_to_existing_file(
        self, *, revision_id: str | UUID | Revision, file_id: str | UUID | File
    ) -> File:
        return self.revision.copy_revision_to_existing_file(
            revision_id=revision_id, file_id=file_id
        )

    def transfer_revision_to_new_file(self, revision_id: str | UUID | Revision) -> File:
        return self.revision.transfer_revision_to_new_file(revision_id)

    def transfer_revision_to_existing_file(
        self, *, revision_id: str | UUID | Revision, file_id: str | UUID | File
    ) -> File:
        return self.revision.transfer_revision_to_existing_file(
            revision_id=revision_id, file_id=file_id
        )

    def transfer_revision_to_new_artifact(
        self, revision_id: str | UUID | Revision, model_id: UUID | Model | str
    ) -> Revision:
        return self.revision.transfer_revision_to_new_artifact(
            revision_id=revision_id, model_id=model_id
        )

    def transfer_revision_to_existing_artifact(
        self, *, revision_id: str | UUID | Revision, artifact_id: str | UUID | Artifact
    ) -> Revision:
        return self.revision.transfer_revision_to_existing_artifact(
            revision_id=revision_id, artifact_id=artifact_id
        )

    def get_system_baseline(self, system_id: UUID) -> SystemBaseline:
        """Fetch the baseline of a system."""
        return self.system.get_system_baseline(system_id)

    def get_system(self, system_id: UUID) -> System:
        """Fetch a system by its ID."""
        return self.system.get_system(system_id)

    def create_system(self, new_system: NewSystem) -> System:
        """Create a new system."""
        return self.system.create_system(new_system)

    def update_system(self, system_id: UUID, update_system: UpdateSystem) -> System:
        """Update an existing system."""
        return self.system.update_system(system_id, update_system)

    def get_configuration(self, configuration_id: UUID) -> SystemConfiguration:
        """Fetch a configuration by its ID."""
        return self.system.get_configuration(configuration_id)

    def create_configuration(
        self, system_id: UUID, new_configuration: NewSystemConfiguration
    ) -> SystemConfiguration:
        """Create a new configuration under the system."""
        return self.system.create_configuration(system_id, new_configuration)

    def get_snapshot(self, snapshot_id: UUID) -> Snapshot:
        """Fetch a snapshot by its ID."""
        return self.system.get_snapshot(snapshot_id)

    def create_snapshot(
        self, configuration_id: UUID, new_snapshot: NewSnapshot
    ) -> ResponseCreateSnapshot:
        """Create a new snapshot under a configuration."""
        return self.system.create_snapshot(configuration_id, new_snapshot)

    def get_tag(self, tag_id: UUID) -> SnapshotTag:
        """Fetch a tag by its ID."""
        return self.system.get_tag(tag_id)

    def create_tag(self, snapshot_id: UUID, new_tag: NewSnapshotTag) -> SnapshotTag:
        """Create a new tag for a snapshot."""
        return self.system.create_tag(snapshot_id, new_tag)

    def update_tag(self, tag_id: UUID, update_tag: UpdateTag) -> SnapshotTag:
        """Updates a tag by its ID with a new snapshot_id."""
        return self.system.update_tag(tag_id=tag_id, update_tag=update_tag)

    def list_systems(
        self,
        archive_status: ArchiveStatus | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSystem:
        """List systems with optional filters."""
        return self.system.list_systems(archive_status, page, size, sort)

    def list_configurations(
        self,
        system_id: UUID,
        archive_status: ArchiveStatus | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSystemConfiguration:
        """List configurations under a system with optional filters."""
        return self.system.list_configurations(
            system_id, archive_status, page, size, sort
        )

    def list_tracked_files(
        self,
        configuration_id: UUID,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageTrackedFile:
        """Lists tracked files for a system or configuration."""
        return self.system.list_tracked_files(
            configuration_id=configuration_id, page=page, size=size, sort=sort
        )

    def list_snapshots(
        self,
        system_id: UUID | None = None,
        configuration_id: UUID | None = None,
        tag: str | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSnapshot:
        """List snapshots with optional filters."""
        return self.system.list_snapshots(
            system_id, configuration_id, tag, page, size, sort
        )

    def list_snapshot_items(
        self,
        snapshot_id: UUID,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSnapshotItem:
        """Lists snapshot items for a given snapshot."""
        return self.system.list_snapshot_items(
            snapshot_id=snapshot_id, page=page, size=size, sort=sort
        )

    def list_tags(
        self,
        system_id: UUID | None = None,
        configuration_id: UUID | None = None,
        snapshot_id: UUID | None = None,
        archive_status: ArchiveStatus | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSnapshotTag:
        """List tags with optional filters."""
        return self.system.list_tags(
            system_id, configuration_id, snapshot_id, archive_status, page, size, sort
        )

    def archive_system(self, system_id: UUID, reason: str | None = None) -> System:
        """Archive a system."""
        return self.system.archive_system(system_id, reason)

    def restore_system(self, system_id: UUID, reason: str | None = None) -> System:
        """Restore a system."""
        return self.system.restore_system(system_id, reason)

    def archive_configuration(
        self, configuration_id: UUID, reason: str | None = None
    ) -> SystemConfiguration:
        """Archive a configuration."""
        return self.system.archive_configuration(configuration_id, reason)

    def restore_configuration(
        self, configuration_id: UUID, reason: str | None = None
    ) -> SystemConfiguration:
        """Restore a configuration."""
        return self.system.restore_configuration(configuration_id, reason)

    def archive_tag(self, tag_id: UUID) -> SnapshotTag:
        """Archive a tag."""
        return self.system.archive_tag(tag_id)

    def restore_tag(self, tag_id: UUID) -> SnapshotTag:
        """Restore a tag."""
        return self.system.restore_tag(tag_id)

    def create_access(
        self,
        access_relationship: AccessRelationship,
    ) -> AccessRelationship:
        return self.access.create_access(access_relationship)

    def list_access(
        self,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
    ) -> list[AccessRelationship]:
        return self.access.list_access(resource_type, resource_id)

    def update_access(
        self,
        subject_type: AccessSubjectType,
        subject_id: UUID | str,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
        update_access_relationship: UpdateAccessRelationship,
    ) -> AccessRelationship:
        return self.access.update_access(
            subject_type,
            subject_id,
            resource_type,
            resource_id,
            update_access_relationship,
        )

    def remove_access(
        self,
        subject_type: AccessSubjectType,
        subject_id: UUID | str,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
    ) -> None:
        return self.access.remove_access(
            subject_type, subject_id, resource_type, resource_id
        )

    def create_access_by_email_for_other_tenants(
        self,
        subject_type: AccessSubjectType,
        email: str,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
        access_relationship: AccessRelation,
    ) -> AccessRelationship:
        """Create access by email for other tenants

        Args:
            subject_type (AccessSubjectType): The subject type
            email (str): The email of the subject
            resource_type (AccessResourceType): The resource type
            resource_id (UUID | str): The resource ID
            access_relationship (AccessRelation): The access relationship

        Returns:
            AccessRelationship: The access relationship
        """
        return self.access.create_access_by_email_for_other_tenants(
            subject_type,
            email,
            resource_type,
            resource_id,
            access_relationship,
        )
