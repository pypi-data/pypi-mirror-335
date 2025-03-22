import abc
import datetime
import logging
import typing
from datetime import timezone
from functools import cached_property
from typing import Union
from uuid import UUID

from istari_digital_client.openapi_client.models import (
    Model as OpenApiModel,
    ModelListItem as OpenApiModelListItem,
    Artifact as OpenApiArtifact,
    Comment as OpenApiComment,
    File as OpenApiFile,
    FileRevision as OpenApiFileRevision,
    Token as OpenApiToken,
    Job as OpenApiJob,
    JobStatus as OpenApiJobStatus,
    Function as OpenApiFunction,
    FunctionSchema as OpenApiFunctionSchema,
    InputSchema as OpenApiInputSchema,
    OutputSchema as OpenApiOutputSchema,
    Module as OpenApiModule,
    ModuleVersion as OpenApiModuleVersion,
    ModuleAuthor as OpenApiModuleAuthor,
    Tool as OpenApiTool,
    ToolVersion as OpenApiToolVersion,
    FileRevisionArchiveStatus as OpenApiFileRevisionArchiveStatus,
    FileArchiveStatus as OpenApiFileArchiveStatus,
    ResourceArchiveStatus as OpenApiResourceArchiveStatus,
    Agent as OpenApiAgent,
    AgentModules as OpenApiAgentModules,
    AgentStatus as OpenApiAgentStatus,
)

if typing.TYPE_CHECKING:
    from istari_digital_client import Client

logger = logging.getLogger("istari-client.managed")

OpenApiEntity = Union[
    OpenApiModel,
    OpenApiModelListItem,
    OpenApiArtifact,
    OpenApiComment,
    OpenApiFile,
    OpenApiFileRevision,
    OpenApiToken,
    OpenApiJob,
    OpenApiJobStatus,
    OpenApiFunction,
    OpenApiFunctionSchema,
    OpenApiInputSchema,
    OpenApiOutputSchema,
    OpenApiModule,
    OpenApiModuleVersion,
    OpenApiModuleAuthor,
    OpenApiTool,
    OpenApiToolVersion,
    OpenApiFileArchiveStatus,
    OpenApiFileRevisionArchiveStatus,
    OpenApiResourceArchiveStatus,
    OpenApiAgent,
    OpenApiAgentModules,
    OpenApiAgentStatus,
]

OpenApiArchiveStatus = Union[
    OpenApiFileArchiveStatus,
    OpenApiFileRevisionArchiveStatus,
    OpenApiResourceArchiveStatus,
]


class Managed(abc.ABC):
    def __init__(self: "Managed", inner: OpenApiEntity, client: "Client") -> None:
        self.inner: OpenApiEntity = inner
        self.client: "Client" = client

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id})"

    @property
    def id(self: "Managed") -> UUID:
        """The id of the object."""
        return UUID(self.inner.id)

    @cached_property
    def created(self: "Managed") -> datetime.datetime:
        """The timestamp of when this token was created and assigned to its parent."""
        ts = self.inner.created

        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)

    @cached_property
    def created_by_id(self: "Managed") -> UUID | None:
        if not hasattr(self.inner, "created_by_id"):
            logger.warning(
                "Inner type %s has no 'created_by_id' property?! Returning None",
                type(self.inner),
            )
            return None

        created_by_id = self.inner.created_by_id
        return UUID(created_by_id) if created_by_id else None
