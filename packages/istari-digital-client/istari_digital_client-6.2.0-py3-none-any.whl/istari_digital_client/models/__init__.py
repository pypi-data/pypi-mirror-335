import abc
import dataclasses
import datetime
import hashlib
import logging
import tempfile
import time
import traceback
import typing
import uuid
from datetime import timezone
from functools import cache
from functools import cached_property
from pathlib import Path
from threading import Lock
from typing import Union, Iterable, Generic, TypeVar
from uuid import UUID

from istari_digital_client.openapi_client import (
    UserType,
    ZitadelUserState,
    InputType,
    OutputType,
)
from istari_digital_client.openapi_client.models.function_status import FunctionStatus
from istari_digital_client.openapi_client.models.module_version_status import (
    ModuleVersionStatus,
)

if typing.TYPE_CHECKING:
    from istari_digital_client import Client

from istari_digital_client.models.properties import Properties
from istari_digital_client.models.properties import PropertiesHaving as PropertiesHaving
from istari_digital_client.models.readable import Readable
from istari_digital_client.models.readable import PathLike as PathLike
from istari_digital_client.models.readable import JSON as JSON
from istari_digital_client.models.managed import Managed, OpenApiArchiveStatus
from istari_digital_client.openapi_client.models import (
    AccessRelationship as OpenApiAccessRelationship,
    AccessRelation,
    AccessResourceType,
    AccessSubjectType,
    ArchiveStatusName,
    Model as OpenApiModel,
    ModelListItem as OpenApiModelListItem,
    PageModelListItem as OpenApiPageModelListItem,
    Artifact as OpenApiArtifact,
    PageArtifact as OpenApiPageArtifact,
    Comment as OpenApiComment,
    PageComment as OpenApiPageComment,
    File as OpenApiFile,
    PageFile as OpenApiPageFile,
    Function as OpenApiFunction,
    PageFunction as OpenApiPageFunction,
    FunctionSchema as OpenApiFunctionSchema,
    FileRevision as OpenApiFileRevision,
    InputSchema as OpenApiInputSchema,
    OutputSchema as OpenApiOutputSchema,
    Source as OpenApiSource,
    Product as OpenApiProduct,
    Job as OpenApiJob,
    JobStatus as OpenApiJobStatus,
    JobStatusName as StatusName,
    PageJob as OpenApiPageJob,
    Module as OpenApiModule,
    PageModule as OpenApiPageModule,
    ModuleType,
    ModuleVersion as OpenApiModuleVersion,
    PageModuleVersion as OpenApiPageModuleVersion,
    ModuleAuthorManifest as OpenApiModuleAuthorManifest,
    ModuleAuthor as OpenApiModuleAuthor,
    PageModuleAuthor as OpenApiPageModuleAuthor,
    PagePersonalAccessToken as OpenApiPagePersonalAccessToken,
    PersonalAccessToken as OpenApiPersonalAccessToken,
    OperatingSystem as OpenApiOperatingSystem,
    PageOperatingSystem as OpenApiPageOperatingSystem,
    Token as OpenApiToken,
    ToolVersion as OpenApiToolVersion,
    PageToolVersion as OpenApiPageToolVersion,
    Tool as OpenApiTool,
    PageTool as OpenApiPageTool,
    User as OpenApiUser,
    ResourceArchiveStatus as OpenApiResourceArchiveStatus,
    FileRevisionArchiveStatus as OpenApiFileRevisionArchiveStatus,
    FileArchiveStatus as OpenApiFileArchiveStatus,
    Archive as OpenApiArchive,
    Restore as OpenApiRestore,
    Agent as OpenApiAgent,
    AgentInformation as OpenApiAgentInformation,
    AgentModules as OpenApiAgentModules,
    AgentModuleVersion as OpenApiAgentModuleVersion,
    AgentStatus as OpenApiAgentStatus,
    AgentStatusName,
    PageAgent as OpenApiPageAgent,
    PageAgentStatus as OpenApiPageAgentStatus,
)

OpenApiResourceLike = Union[
    OpenApiModel, OpenApiArtifact, OpenApiComment, OpenApiJob, OpenApiModelListItem
]

OpenApiResource = Union[OpenApiModel, OpenApiArtifact, OpenApiComment, OpenApiJob]

OpenApiPage = Union[
    OpenApiPageModelListItem,
    OpenApiPageFile,
    OpenApiPageFunction,
    OpenApiPageJob,
    OpenApiPageAgent,
    OpenApiPageAgentStatus,
    OpenApiPageArtifact,
    OpenApiPageComment,
    OpenApiPageModule,
    OpenApiPageModuleVersion,
    OpenApiPageModuleAuthor,
    OpenApiPagePersonalAccessToken,
    OpenApiPageOperatingSystem,
    OpenApiPageToolVersion,
    OpenApiPageTool,
]

logger = logging.getLogger("istari-client.models")


class ReadError(IOError):
    pass


class CacheError(Exception):
    pass


class InvalidChecksumError(ValueError):
    pass


class AgentStatus(Managed):
    def __init__(self, inner: OpenApiAgentStatus, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiAgentStatus = inner

    @cached_property
    def agent_id(self: "AgentStatus") -> UUID:
        return UUID(self.inner.agent_id)

    @cached_property
    def message(self: "AgentStatus") -> str | None:
        return self.inner.message

    @cached_property
    def name(self: "AgentStatus") -> AgentStatusName:
        return self.inner.name


class AgentModules(Managed):
    def __init__(self, inner: OpenApiAgentModules, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiAgentModules = inner

    @cached_property
    def agent_id(self: "AgentModules") -> UUID:
        return UUID(self.inner.agent_id)

    @cached_property
    def module_versions(self: "AgentModules") -> list[OpenApiAgentModuleVersion]:
        return self.inner.module_versions


class Agent(Managed):
    def __init__(self, inner: OpenApiAgent, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiAgent = inner

    @cached_property
    def agent_identifier(self: "Agent") -> str:
        return self.inner.agent_identifier

    @cached_property
    def information(self: "Agent") -> OpenApiAgentInformation | None:
        if self.inner.information_history:
            return self.inner.information_history[-1]
        else:
            return None

    @cached_property
    def agent_version(self: "Agent") -> str | None:
        return self.information.agent_version if self.information else None

    @cached_property
    def host_os(self: "Agent") -> str | None:
        return self.information.host_os if self.information else None

    @cached_property
    def information_history(self: "Agent") -> list[OpenApiAgentInformation]:
        return self.inner.information_history if self.inner.information_history else []

    @cached_property
    def modules(self: "Agent") -> OpenApiAgentModules | None:
        if self.inner.modules_history:
            return self.inner.modules_history[-1]
        else:
            return None

    @cached_property
    def modules_history(self: "Agent") -> list[AgentModules]:
        if self.inner.modules_history:
            return [
                AgentModules(a_m, self.client) for a_m in self.inner.modules_history
            ]
        else:
            return []

    @cached_property
    def status(self: "Agent") -> AgentStatus | None:
        if self.inner.status_history:
            return AgentStatus(self.inner.status_history[-1], self.client)
        else:
            return None

    @cached_property
    def status_history(self: "Agent") -> list[AgentStatus]:
        if self.inner.status_history:
            return [AgentStatus(a_s, self.client) for a_s in self.inner.status_history]
        else:
            return []


class ArchiveStatus(Managed):
    def __init__(self, inner: OpenApiArchiveStatus, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiArchiveStatus = inner

    @property
    def name(self: "ArchiveStatus") -> ArchiveStatusName:
        return self.inner.name

    @property
    def reason(self: "ArchiveStatus") -> str | None:
        return self.inner.reason


class AccessRelationship:
    def __init__(
        self: "AccessRelationship",
        subject_type: AccessSubjectType,
        subject_id: UUID | str,
        relation: AccessRelation,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
    ) -> None:
        if isinstance(subject_id, UUID):
            subject_id = str(subject_id)

        if isinstance(resource_id, UUID):
            resource_id = str(resource_id)

        self.inner: OpenApiAccessRelationship = OpenApiAccessRelationship(
            subject_type=subject_type,
            subject_id=subject_id,
            relation=relation,
            resource_type=resource_type,
            resource_id=resource_id,
        )

    @property
    def subject_type(self: "AccessRelationship") -> AccessSubjectType:
        return self.inner.subject_type

    @property
    def subject_id(self: "AccessRelationship") -> UUID:
        return UUID(self.inner.subject_id)

    @property
    def relation(self: "AccessRelationship") -> AccessRelation:
        return self.inner.relation

    @property
    def resource_type(self: "AccessRelationship") -> AccessResourceType:
        return self.inner.resource_type

    @property
    def resource_id(self: "AccessRelationship") -> UUID:
        return UUID(self.inner.resource_id)


class FileArchiveStatus(ArchiveStatus):
    def __init__(self, inner: OpenApiFileArchiveStatus, client: "Client") -> None:
        super().__init__(inner, client)
        self.client = client
        self.inner: OpenApiFileArchiveStatus = inner

    @cached_property
    def file_id(self) -> UUID:
        return UUID(self.inner.file_id)

    @cached_property
    def file(self) -> "File":
        return self.client.get_file(self.file_id)


class File(Managed, Readable):
    def __init__(self, inner: OpenApiFile, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiFile = inner
        self.client: "Client" = client
        if not isinstance(self.inner, OpenApiFile):
            raise TypeError(
                "inner must be instance of OpenApiFile, not " + str(type(self.inner))
            )

    @cached_property
    def resource_id(self) -> UUID | None:
        return UUID(self.inner.resource_id) if self.inner.resource_id else None

    @cached_property
    def resource_type(self: "File") -> type["ResourceLike"] | None:
        name = self.inner.resource_type
        if not name:
            return None
        t = to_resource_type(name)
        if not t:
            raise TypeError("Unknown resource type: '" + str(name) + "'")
        return t

    @cached_property
    def resource(self: "File") -> Union["ResourceLike", None]:
        if self.resource_id and self.resource_type:
            return self.client.get_resource(self.resource_type, self.resource_id)
        return None

    @property
    def properties(self: "File") -> "Properties":
        return self.revision.properties_token.properties

    def read_bytes(self) -> bytes:
        return self.revision.read_bytes()

    @property
    def revision(self: "File") -> "Revision":
        """Property getter for the current revision of the file

        Note -- this is the same as accessing .revisions[-1]
        """
        return self.revisions[-1]

    @cached_property
    def revisions(self) -> list["Revision"]:
        """The list of tokens that represent both the current and all previous contents of the object file.

        Sorted in chronological order, the last item will always be the most recent.
        """
        return [Revision(r, self.client) for r in self.inner.revisions]

    @cached_property
    def archive_status_history(self) -> list[FileArchiveStatus]:
        return [
            FileArchiveStatus(status, self.client)
            for status in self.inner.archive_status_history
        ]

    @property
    def archive_status(self) -> FileArchiveStatus:
        return self.archive_status_history[-1]


class Derivation:
    def __init__(self, inner: OpenApiSource | OpenApiProduct, client: "Client") -> None:
        self.inner: OpenApiSource | OpenApiProduct = inner
        self.client: "Client" = client

    @cached_property
    def revision_id(self: "Derivation") -> UUID:
        """The revision id for the derivation (source or product)."""
        return UUID(self.inner.revision_id)

    @cached_property
    def revision(self: "Derivation") -> "Revision":
        """The derivation (source or product) revision."""
        return self.client.get_revision(self.revision_id)

    @cached_property
    def file_id(self: "Derivation") -> UUID | None:
        """The derivation (source or product) revision file id."""
        return UUID(self.inner.file_id) if self.inner.file_id else None

    @cached_property
    def file(self: "Derivation") -> File | None:
        """The derivation (source or product) revision file."""
        return self.client.get_file(self.file_id) if self.file_id else None

    @cached_property
    def resource(self: "Derivation") -> Union["ResourceLike", None]:
        """The derivation (source or product) revision file resource (if any)."""
        if self.resource_id and self.resource_type:
            return self.client.get_resource(self.resource_type, self.resource_id)
        return None

    @cached_property
    def relationship_identifier(self: "Derivation") -> str | None:
        return self.inner.relationship_identifier

    @cached_property
    def resource_id(self: "Derivation") -> UUID | None:
        """The derivation (source or product) revision file resource id (if any)."""
        return UUID(self.inner.resource_id) if self.inner.revision_id else None

    @cached_property
    def resource_type(self: "Derivation") -> type["ResourceLike"] | None:
        resource_type: type[ResourceLike] | None = None
        if self.inner.resource_type:
            resource_type = (
                to_resource_type(str(self.inner.resource_type))
                if self.inner.resource_type
                else None
            )
        if not resource_type:
            raise TypeError(
                "Unknown resource type: '" + str(self.inner.resource_type) + "'"
            )
        return resource_type


class Source(Derivation):
    def __init__(self, inner: OpenApiSource, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiSource = inner


class Product(Derivation):
    def __init__(self, inner: OpenApiProduct, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiProduct = inner


class RevisionArchiveStatus(ArchiveStatus):
    def __init__(
        self, inner: OpenApiFileRevisionArchiveStatus, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.client = client
        self.inner: OpenApiFileRevisionArchiveStatus = inner

    @cached_property
    def revision_id(self) -> UUID:
        return UUID(self.inner.file_revision_id)

    @cached_property
    def revision(self) -> "Revision":
        return self.client.get_revision(self.revision_id)


class Revision(Managed, Readable):
    def __init__(self, inner: OpenApiFileRevision, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiFileRevision = inner
        self.client: "Client" = client

    @cached_property
    def file_id(self) -> UUID:
        """The id of the the revision belongs to."""
        return UUID(self.inner.file_id)

    @cached_property
    def file(self) -> "File":
        """The file the revision belongs to."""
        return self.client.get_file(self.file_id)

    @cached_property
    def content_token(self) -> "Token":
        """The revision file content token."""
        return Token(self.inner.content_token, self.client)

    @cached_property
    def properties_token(self: "Revision") -> "Token":
        """The revision file properties token."""
        return Token(self.inner.properties_token, self.client)

    def read_bytes(self: "Revision") -> bytes:
        """The revision file content."""
        return self.content_token.read_bytes()

    @property
    def properties(self: "Revision") -> "Properties":
        """The revision file properties"""
        return self.properties_token.properties

    @cached_property
    def sources(self: "Revision") -> list["Source"]:
        """The sources the revision was derived from."""
        if self.inner.sources is None:
            raise TypeError("No products found in revision.")
        else:
            sources = self.inner.sources
        return [Source(source, self.client) for source in sources]

    def source_revision_ids(self: "Revision") -> list[UUID]:
        """The source revision ids the revision was derived from."""
        return [source.revision_id for source in self.sources]

    @cached_property
    def products(self: "Revision") -> list["Product"]:
        """The products derived from the revision. """ ""
        if self.inner.products is None:
            raise TypeError("No products found in revision.")
        else:
            products = self.inner.products
        return [Product(product, self.client) for product in products]

    def product_revision_ids(self: "Revision") -> list[UUID]:
        """The revision ids of the products derived from the revision."""
        return [product.revision_id for product in self.products]

    @cached_property
    def archive_status_history(self) -> list[RevisionArchiveStatus]:
        return [
            RevisionArchiveStatus(status, self.client)
            for status in self.inner.archive_status_history
        ]

    @property
    def archive_status(self) -> RevisionArchiveStatus:
        return self.archive_status_history[-1]


class Token(Managed, Readable):
    def __init__(
        self,
        inner: OpenApiToken,
        client: "Client",
        read_retry_count: int = 2,
        retry_backoff_interval_seconds: int = 1,
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiToken = inner
        self.client: "Client" = client
        self._read_retry_count: int = read_retry_count
        self._read_retry_backoff_interval: int = retry_backoff_interval_seconds
        self._cache_path_lock = Lock()
        self._cache_path_lock_timeout = (
            self._read_retry_count * self._read_retry_backoff_interval
        )
        self._filesystem_cache_hits = 0
        self._filesystem_cache_misses = 0
        self._filesystem_cache_puts = 0

    def __del__(self):
        """Delete cached content."""
        if self._cache_path is not None:
            self._cache_path.unlink(missing_ok=True)

    @cached_property
    def _log_msg_pfx(self) -> str:
        return f"token {self.id} -"

    def _cache_identifier(self, size: int = 16) -> str:
        hash = hashlib.shake_256()
        hash.update(self.sha.encode("utf-8"))
        hash.update(self.salt.encode("utf-8"))
        return hash.hexdigest(size)

    @cached_property
    def _cache_dir(self) -> Path:
        subdir = self._cache_identifier(2)
        dir = self.client.configuration.filesystem_cache_root / subdir
        dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        return dir

    @cached_property
    def _cache_name(self) -> str:
        return self._cache_identifier(32)

    @cached_property
    def _cache_path(self) -> Path:
        return self._cache_dir / self._cache_name

    def _cache_dir_mktemp(self) -> Path:
        return Path(
            tempfile.mktemp(
                suffix=str(uuid.uuid4()) + ".tmp",
                prefix=self._cache_name,
                dir=self._cache_dir,
            )
        )

    def _checksum_verified(self, data: bytes) -> bytes:
        data = self._cache_path.read_bytes()
        hash = hashlib.sha384()
        hash.update(data)
        hash.update(self.salt.encode("utf-8"))
        actual = hash.hexdigest()
        expected = self.sha
        if not actual == expected:
            msg = f"Token data content checksum is invalid ({actual} != {expected})"
            raise InvalidChecksumError(msg)
        return data

    def _checksum_verified_cache_read(self) -> bytes:
        if not self._cache_path.exists():
            raise FileNotFoundError(self._cache_path)
        data = self._checksum_verified(self._cache_path.read_bytes())
        return data

    def _filesystem_caching_read_bytes(self) -> bytes:
        with self._cache_path_lock:
            try:
                data = self._checksum_verified_cache_read()
                self._filesystem_cache_hits += 1
                return data
            except Exception:
                self._filesystem_cache_misses += 1
                logger.debug("%s", traceback.format_exc())
                if not self._cache_dir.exists():
                    self._cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
                if self._cache_path.exists():
                    self._cache_path.unlink(missing_ok=True)
                temp_path = Path(self._cache_dir_mktemp())
                logger.debug("%s downloading to %s", self._log_msg_pfx, temp_path)
                data = self.client.read_contents(self)
                temp_path.write_bytes(data)
                size = temp_path.stat().st_size
                temp_path.replace(self._cache_path)
                logger.debug(
                    "%s downloaded contents to filesystem cache (size: %d): %s",
                    self._log_msg_pfx,
                    size,
                    self._cache_path,
                )
                self._filesystem_cache_puts += 1
                return self._checksum_verified(data)

    def read_bytes(self) -> bytes:
        attempt = 0
        last_exception: Exception | None = None
        while attempt < self._read_retry_count:
            attempt += 1
            if attempt > 1:
                time.sleep(self._read_retry_backoff_interval * attempt)
            logger.debug(
                "%s %s read (attempt %d of %d)",
                self._log_msg_pfx,
                "attempting" if attempt == 1 else "attempting to retry",
                attempt,
                self._read_retry_count,
            )
            try:
                if self.client.configuration.filesystem_cache_enabled:
                    return self._filesystem_caching_read_bytes()
                return self.client.read_contents(self)
            except Exception as e:
                last_exception = e
                logger.error(
                    "%s, exception caught reading token data  (attempt %d of %d): %s",
                    self._log_msg_pfx,
                    attempt,
                    self._read_retry_count + 1,
                    str(e),
                )
        last_exception = last_exception or ReadError("unknown")
        raise ReadError("retry count exceeded") from last_exception

    @cached_property
    def properties(self: "Token") -> "Properties":
        return self.client.read_properties(self)

    @property
    def sha(self: "Token") -> str:
        """The salted sha of the token contents."""
        return self.inner.sha

    @property
    def salt(self: "Token") -> str:
        """The salt used when the sha property was computed."""
        return self.inner.salt


class ResourceLike(Managed, Readable, abc.ABC):
    def __init__(
        self: "ResourceLike", inner: OpenApiResourceLike, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiResourceLike = inner

    @property
    def properties(self: "ResourceLike") -> "Properties":
        """The resource file's current revision properties."""
        return self.file.properties

    def read_bytes(self) -> bytes:
        """Reads the content of the current revision of the resource file."""
        return self.file.read_bytes()

    @property
    def revision(self: "ResourceLike") -> "Revision":
        """The current revision of the resource file."""
        return self.file.revision

    @property
    def revisions(self: "ResourceLike") -> list["Revision"]:
        """All the revisions for the resource file, in chronological order."""
        return self.file.revisions

    @cached_property
    def file(self: "ResourceLike") -> "File":
        """The resources' file."""
        return File(self.inner.file, self.client)  # type: ignore[union-attr]

    @abc.abstractproperty
    def comments(self: "ResourceLike") -> list["Comment"]:
        raise NotImplementedError("comments property must be implemented in subclasses")


class Resource(ResourceLike):
    def __init__(
        self: "Resource",
        inner: OpenApiResource,
        client: "Client",
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiResource = inner

    @property
    def comments(self) -> list["Comment"]:
        return [Comment(c, self.client) for c in self.inner.comments]


class CommentArchiveStatus(ArchiveStatus):
    def __init__(self, inner: OpenApiResourceArchiveStatus, client: "Client") -> None:
        super().__init__(inner, client)
        self.client = client
        self.inner: OpenApiResourceArchiveStatus = inner

    @cached_property
    def comment_id(self) -> UUID:
        return UUID(self.inner.resource_id)

    @cached_property
    def comment(self) -> "Comment":
        return self.client.get_comment(self.comment_id)


class Comment(Resource):
    def __init__(self: "Comment", inner: OpenApiComment, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiComment = inner
        if not isinstance(self.inner, OpenApiComment):
            raise TypeError(str(self.inner) + " (" + str(type(self.inner)) + ")")
        self.client: Client = client

    @cached_property
    def resource_id(self: "Comment") -> UUID:
        """The ID of the owning resource"""
        return UUID(self.inner.resource_id)

    @cached_property
    def archive_status_history(self) -> list[CommentArchiveStatus]:
        return [
            CommentArchiveStatus(status, self.client)
            for status in self.inner.archive_status_history
        ]

    @property
    def archive_status(self) -> CommentArchiveStatus:
        return self.archive_status_history[-1]


class ModelArchiveStatus(ArchiveStatus):
    def __init__(self, inner: OpenApiResourceArchiveStatus, client: "Client") -> None:
        super().__init__(inner, client)
        self.client = client
        self.inner: OpenApiResourceArchiveStatus = inner

    @cached_property
    def model_id(self) -> UUID:
        return UUID(self.inner.resource_id)

    @cached_property
    def model(self) -> "Model":
        return self.client.get_model(self.model_id)


class ModelListItem(ResourceLike):
    def __init__(
        self: "ModelListItem", inner: OpenApiModelListItem, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiModelListItem = inner
        self.client: "Client" = client
        if not isinstance(self.inner, OpenApiModelListItem):
            raise TypeError(str(self.inner) + " (" + str(type(self.inner)) + ")")

    @cached_property
    def model(self: "ModelListItem") -> "Model":
        return self.client.get_model(self.inner.id)

    @property
    def comments(self: "ModelListItem") -> list[Comment]:
        return self.model.comments

    @property
    def artifacts(self: "ModelListItem") -> list["Artifact"]:
        """The list of artifacts that belong to the model."""
        return self.model.artifacts

    @property
    def archive_status_history(self: "ModelListItem") -> list[ModelArchiveStatus]:
        return self.model.archive_status_history

    @property
    def archive_status(self: "ModelListItem") -> ModelArchiveStatus:
        return self.model.archive_status


class Model(Resource):
    def __init__(self: "Model", inner: OpenApiModel, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiModel = inner
        self.client: "Client" = client
        if not isinstance(self.inner, OpenApiModel):
            raise TypeError(str(self.inner) + " (" + str(type(self.inner)) + ")")

    @cached_property
    def artifacts(self: "Model") -> list["Artifact"]:
        """The list of artifacts that belong to the model."""
        return [Artifact(a, self.client) for a in self.inner.artifacts]

    @cached_property
    def archive_status_history(self) -> list[ModelArchiveStatus]:
        return [
            ModelArchiveStatus(status, self.client)
            for status in self.inner.archive_status_history
        ]

    @property
    def archive_status(self) -> ModelArchiveStatus:
        return self.archive_status_history[-1]


class ArtifactArchiveStatus(ArchiveStatus):
    def __init__(self, inner: OpenApiResourceArchiveStatus, client: "Client") -> None:
        super().__init__(inner, client)
        self.client = client
        self.inner: OpenApiResourceArchiveStatus = inner

    @cached_property
    def artifact_id(self) -> UUID:
        return UUID(self.inner.resource_id)

    @cached_property
    def artifact(self) -> "Artifact":
        return self.client.get_artifact(self.artifact_id)


class Artifact(Resource):
    def __init__(self: "Artifact", inner: OpenApiArtifact, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiArtifact = inner
        self.client: "Client" = client
        if not isinstance(self.inner, OpenApiArtifact):
            raise TypeError(str(self.inner) + " (" + str(type(self.inner)) + ")")

    @cached_property
    def archive_status_history(self) -> list[ArtifactArchiveStatus]:
        return [
            ArtifactArchiveStatus(status, self.client)
            for status in self.inner.archive_status_history
        ]

    @property
    def archive_status(self) -> ArtifactArchiveStatus:
        return self.archive_status_history[-1]

    @cached_property
    def model_id(self: "Artifact") -> UUID:
        """The id of the model this artifact belongs to."""
        return UUID(self.inner.model_id)

    @cached_property
    def model(self: "Artifact") -> "Model":
        return self.client.get_model(self.model_id)


class Job(Resource):
    def __init__(self: "Job", inner: OpenApiJob, client: "Client") -> None:
        super().__init__(inner, client)
        self.client: "Client" = client
        self.inner: OpenApiJob = inner

    @cached_property
    def model_id(self: "Job") -> UUID:
        return UUID(self.inner.model_id)

    @cached_property
    def function(self: "Job") -> "Function":
        return Function(self.inner.function, self.client)

    @property
    def status(self: "Job") -> "JobStatus":
        return self.status_history[-1]

    @cached_property
    def status_history(self: "Job") -> list["JobStatus"]:
        if self.inner.status_history is None:
            raise TypeError("No status history found in job.")
        else:
            status_history = self.inner.status_history

        return [JobStatus(status, self.client) for status in status_history]

    @cached_property
    def model(self: "Job") -> "Model":
        return self.client.get_model(self.model_id)


class JobStatus(Managed):
    def __init__(self: "JobStatus", inner: OpenApiJobStatus, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiJobStatus = inner
        self.client: "Client" = client

    @cached_property
    def job_id(self) -> UUID:
        return UUID(self.inner.job_id)

    @cached_property
    def job(self) -> "Job":
        return self.client.get_job(self.job_id)

    @cached_property
    def name(self) -> StatusName:
        return self.inner.name

    @property
    def agent_identifier(self) -> str | None:
        return self.inner.agent_identifier


class OperatingSystem:
    def __init__(
        self: "OperatingSystem",
        inner: OpenApiOperatingSystem,
    ) -> None:
        self.inner: OpenApiOperatingSystem = inner

    @property
    def id(self) -> UUID:
        return UUID(self.inner.id)

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def created(self) -> datetime.datetime:
        ts = self.inner.created

        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)


class OperatingSystemPage:
    def __init__(
        self: "OperatingSystemPage",
        inner: OpenApiPageOperatingSystem,
    ) -> None:
        self.inner: OpenApiPageOperatingSystem = inner

    @property
    def items(self) -> list[OperatingSystem]:
        return [OperatingSystem(os) for os in self.inner.items]


class ToolVersion(Managed):
    def __init__(
        self,
        inner: OpenApiToolVersion,
        client: "Client",
    ) -> None:
        super().__init__(inner, client)
        self.inner: "OpenApiToolVersion" = inner

    @property
    def id(self) -> UUID:
        return UUID(self.inner.id)

    @property
    def created(self) -> datetime.datetime:
        ts = self.inner.created

        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)

    @property
    def tool_version(self) -> str:
        return self.inner.tool_version


class Tool(Managed):
    def __init__(
        self: "Tool",
        inner: OpenApiTool,
        client: "Client",
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiTool = inner
        self.client: "Client" = client

    @property
    def id(self) -> UUID:
        return UUID(self.inner.id)

    @property
    def created(self) -> datetime.datetime:
        ts = self.inner.created

        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def tool_versions(self) -> list[ToolVersion] | None:
        return (
            [ToolVersion(tv, self.client) for tv in self.inner.tool_versions]
            if self.inner.tool_versions is not None
            else None
        )


class InputSchema(Managed):
    def __init__(
        self: "InputSchema", inner: OpenApiInputSchema, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiInputSchema = inner
        self.client: "Client" = client

    @property
    def key(self) -> str:
        return self.inner.key

    @property
    def type(self) -> InputType:
        return self.inner.type

    @property
    def validation_types(self) -> list[str] | None:
        return self.inner.validation_types


class OutputSchema(Managed):
    def __init__(
        self: "OutputSchema", inner: OpenApiOutputSchema, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiOutputSchema = inner
        self.client: "Client" = client

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def type(self) -> OutputType:
        return self.inner.type

    @property
    def required(self) -> bool:
        return self.inner.required


class FunctionSchema(Managed):
    def __init__(
        self: "FunctionSchema", inner: OpenApiFunctionSchema, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiFunctionSchema = inner
        self.client: "Client" = client

    @property
    def inputs(self) -> list[InputSchema] | None:
        return (
            [InputSchema(i, self.client) for i in self.inner.inputs]
            if self.inner.inputs
            else None
        )

    @property
    def outputs(self) -> list[OutputSchema] | None:
        return (
            [OutputSchema(o, self.client) for o in self.inner.outputs]
            if self.inner.outputs
            else None
        )


class Function(Managed):
    def __init__(self: "Function", inner: OpenApiFunction, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiFunction = inner
        self.client: "Client" = client

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def entrypoint(self) -> str:
        return self.inner.entrypoint

    @property
    def function_schema(self) -> str | None:
        return self.inner.function_schema

    @property
    def run_command(self) -> str:
        return self.inner.run_command

    @property
    def tool_name(self) -> str | None:
        return self.inner.tool_name

    @property
    def tool_versions(self) -> list[ToolVersion] | None:
        return (
            [ToolVersion(tv, self.client) for tv in self.inner.tool_versions]
            if self.inner.tool_versions is not None
            else None
        )

    @property
    def operating_systems(self) -> list[OperatingSystem] | None:
        return (
            [OperatingSystem(os) for os in self.inner.operating_systems]
            if self.inner.operating_systems is not None
            else None
        )

    @property
    def status(self) -> FunctionStatus:
        return self.inner.status


class Module(Managed):
    def __init__(
        self: "Module",
        inner: OpenApiModule,
        client: "Client",
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiModule = inner
        self.client: "Client" = client

    @property
    def id(self) -> UUID:
        return UUID(self.inner.id)

    @property
    def created(self) -> datetime.datetime:
        ts = self.inner.created

        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def module_type(self) -> ModuleType:
        return self.inner.module_type

    @property
    def internal(self) -> bool:
        return self.inner.internal

    @property
    def tool(self) -> str | None:
        return self.inner.tool

    @property
    def module_versions(self) -> list["ModuleVersion"] | None:
        return (
            [ModuleVersion(mv, self.client) for mv in self.inner.module_versions]
            if self.inner.module_versions is not None
            else None
        )


class ModuleVersion(Managed):
    def __init__(self, inner: OpenApiModuleVersion, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiModuleVersion = inner
        self.client: "Client" = client

    @property
    def id(self) -> UUID:
        return UUID(self.inner.id)

    @property
    def created(self) -> datetime.datetime:
        ts = self.inner.created

        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)

    @property
    def module_version(self) -> str:
        return self.inner.module_version

    @property
    def check_sum(self) -> str:
        return self.inner.check_sum

    @property
    def agent_version(self) -> str:
        return self.inner.agent_version

    @property
    def module_id(self) -> UUID:
        return UUID(self.inner.module_id)

    @property
    def tool_versions(self) -> list[str] | None:
        return self.inner.tool_versions

    @property
    def operating_systems(self) -> list[str] | None:
        return self.inner.operating_systems

    @property
    def authors(self) -> list["ModuleAuthor"] | None:
        return (
            [ModuleAuthor(a, self.client) for a in self.inner.authors]
            if self.inner.authors is not None
            else None
        )

    @property
    def functions(self) -> dict[str, list[Function]] | None:
        return (
            {
                k: [Function(f, self.client) for f in v]
                for k, v in self.inner.functions.items()
            }
            if self.inner.functions is not None
            else None
        )

    @property
    def status(self) -> ModuleVersionStatus:
        return self.inner.status


class ModuleAuthor(Managed):
    def __init__(
        self,
        inner: OpenApiModuleAuthor,
        client: "Client",
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiModuleAuthor = inner

    @property
    def id(self) -> UUID:
        return UUID(self.inner.id)

    @property
    def created(self) -> datetime.datetime:
        ts = self.inner.created

        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def email(self) -> str:
        return self.inner.email


class ModuleAuthorManifest:
    def __init__(self, inner: OpenApiModuleAuthorManifest) -> None:
        self.inner: OpenApiModuleAuthorManifest = inner

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def email(self) -> str:
        return self.inner.email


R = TypeVar("R", bound="Managed")


class Page(Generic[R], abc.ABC):
    def __init__(self: "Page[R]", inner: OpenApiPage, istari: "Client") -> None:
        self.inner: OpenApiPage = inner
        self.client: "Client" = istari

    @property
    def page(self: "Page[R]") -> int | None:
        """What page number this page is in the set."""
        return self.inner.page

    @property
    def size(self: "Page[R]") -> int | None:
        """The number of items in this page."""
        return self.inner.size

    @property
    def pages(self: "Page[R]") -> int | None:
        """The total number of pages in the set."""
        return self.inner.pages

    @property
    def total(self: "Page[R]") -> int | None:
        """The total number of items in the set."""
        return self.inner.total

    @property
    @abc.abstractmethod
    def items(self: "Page[R]") -> list[R]: ...


class AgentPage(Page[Agent]):
    """A page of agents returned from the backend."""

    def __init__(self: "AgentPage", inner: OpenApiPageAgent, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageAgent = inner

    @property
    def items(self) -> list[Agent]:
        """The retrieved agents in the page."""
        return [Agent(a, self.client) for a in self.inner.items]


class AgentStatusPage(Page[AgentStatus]):
    """A page of agent statuses returned from the backend."""

    def __init__(
        self: "AgentStatusPage", inner: OpenApiPageAgentStatus, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageAgentStatus = inner

    @property
    def items(self) -> list[AgentStatus]:
        """The retrieved agent statuses in the page."""
        return [AgentStatus(a_s, self.client) for a_s in self.inner.items]


class ArtifactPage(Page[Artifact]):
    """A page of models returned from the backend."""

    def __init__(
        self: "ArtifactPage", inner: OpenApiPageArtifact, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageArtifact = inner

    @property
    def items(self) -> list[Artifact]:
        """The retrieved models in the page."""
        return [Artifact(m, self.client) for m in self.inner.items]


class CommentPage(Page[Comment]):
    """A page of models returned from the backend."""

    def __init__(
        self: "CommentPage", inner: OpenApiPageComment, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageComment = inner

    @property
    def items(self) -> list["Comment"]:
        """The retrieved models in the page."""
        return [Comment(m, self.client) for m in self.inner.items]


class FunctionPage(Page[Function]):
    def __init__(
        self: "FunctionPage",
        inner: OpenApiPageFunction,
        client: "Client",
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageFunction = inner

    @property
    def items(self) -> list["Function"]:
        return [Function(f, self.client) for f in self.inner.items]


class JobPage(Page[Job]):
    """A page of models returned from the backend."""

    def __init__(self: "JobPage", inner: OpenApiPageJob, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageJob = inner

    @property
    def items(self) -> list[Job]:
        """The retrieved models in the page."""
        return [Job(m, self.client) for m in self.inner.items]


class ModelListItemPage(Page[ModelListItem]):
    """A page of models returned from the backend."""

    def __init__(
        self: "ModelListItemPage", inner: OpenApiPageModelListItem, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageModelListItem = inner

    @property
    def items(self) -> list[ModelListItem]:
        """The retrieved models in the page."""
        return [ModelListItem(m, self.client) for m in self.inner.items]


class FilePage(Page[File]):
    """A page of files returned from the backend."""

    def __init__(self: "FilePage", inner: OpenApiPageFile, client: "Client") -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageFile = inner

    @property
    def items(self) -> list[File]:
        """The retrieved files in the page."""
        return [File(m, self.client) for m in self.inner.items]


class ModulePage(Page[Module]):
    def __init__(
        self: "ModulePage", inner: OpenApiPageModule, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageModule = inner

    @property
    def items(self) -> list[Module]:
        """The retrieved models in the page."""
        return [Module(m, self.client) for m in self.inner.items]


class ModuleVersionPage(Page[ModuleVersion]):
    def __init__(
        self: "ModuleVersionPage", inner: OpenApiPageModuleVersion, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageModuleVersion = inner

    @property
    def items(self) -> list[ModuleVersion]:
        return [ModuleVersion(mv, self.client) for mv in self.inner.items]


class ModuleAuthorPage(Page[ModuleAuthor]):
    def __init__(
        self: "ModuleAuthorPage", inner: OpenApiPageModuleAuthor, client: "Client"
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageModuleAuthor = inner

    @property
    def items(self) -> list[ModuleAuthor]:
        return [ModuleAuthor(ma, self.client) for ma in self.inner.items]


class ToolPage(Page[Tool]):
    def __init__(
        self: "ToolPage",
        inner: OpenApiPageTool,
        client: "Client",
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageTool = inner

    @property
    def items(self) -> list[Tool]:
        return [Tool(t, self.client) for t in self.inner.items]


class ToolVersionPage(Page[ToolVersion]):
    def __init__(
        self: "ToolVersionPage",
        inner: OpenApiPageToolVersion,
        client: "Client",
    ) -> None:
        super().__init__(inner, client)
        self.inner: OpenApiPageToolVersion = inner

    @property
    def items(self) -> list[ToolVersion]:
        return [ToolVersion(tv, self.client) for tv in self.inner.items]


class PersonalAccessToken:
    def __init__(
        self: "PersonalAccessToken",
        inner: OpenApiPersonalAccessToken,
    ) -> None:
        self.inner: OpenApiPersonalAccessToken = inner

    @property
    def id(self) -> UUID:
        return UUID(self.inner.id)

    @property
    def created(self) -> datetime.datetime:
        ts = self.inner.created

        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)

    @property
    def machine_user_id(self) -> UUID:
        return UUID(self.inner.machine_user_id)

    @property
    def token(self) -> str:
        return self.inner.token

    @property
    def token_id(self) -> UUID:
        return UUID(self.inner.token_id)

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def created_by_id(self) -> UUID:
        return UUID(self.inner.created_by_id)


class PersonalAccessTokenPage:
    def __init__(
        self: "PersonalAccessTokenPage", inner: OpenApiPagePersonalAccessToken
    ) -> None:
        self.inner: OpenApiPagePersonalAccessToken = inner

    @property
    def items(self) -> list[PersonalAccessToken]:
        return [PersonalAccessToken(pat) for pat in self.inner.items]


class User:
    def __init__(
        self,
        inner: OpenApiUser,
    ) -> None:
        self.inner: OpenApiUser = inner

    @property
    def id(self) -> UUID:
        return UUID(self.inner.id)

    @property
    def created(self) -> datetime.datetime:
        ts = self.inner.created
        if ts.tzinfo == timezone.utc:
            return ts
        return ts.astimezone(timezone.utc)

    @property
    def provider_name(self) -> str:
        return self.inner.provider_name

    @property
    def provider_user_id(self) -> UUID:
        return UUID(self.inner.provider_user_id)

    @property
    def user_type(self) -> UserType:
        return self.inner.user_type

    @property
    def personal_access_tokens(self) -> list[PersonalAccessToken]:
        return [PersonalAccessToken(pat) for pat in self.inner.personal_access_tokens]

    @property
    def provider_user_state(self) -> ZitadelUserState | None:
        return self.inner.provider_user_state

    @property
    def user_name(self) -> str | None:
        return self.inner.user_name

    @property
    def display_name(self) -> str | None:
        return self.inner.display_name

    @property
    def first_name(self) -> str | None:
        return self.inner.first_name

    @property
    def last_name(self) -> str | None:
        return self.inner.last_name

    @property
    def email(self) -> str | None:
        return self.inner.email

    @property
    def machine_name(self) -> str | None:
        return self.inner.machine_name

    @property
    def machine_description(self) -> str | None:
        return self.inner.machine_description


@dataclasses.dataclass
class NewSource:
    revision_id: UUID
    relationship_identifier: str | None = None

    @classmethod
    def from_source_input(
        cls, param: Union[ResourceLike, File, Revision, UUID, str, "NewSource"]
    ) -> "NewSource":
        if isinstance(param, NewSource):
            return param
        return NewSource(revision_id=UUID(to_openapi_source_revision_id(param)))


def to_restore_reason(reason: str | None) -> OpenApiArchive | None:
    if reason is None:
        return None
    return OpenApiArchive(reason=reason)


def to_openapi_archive(reason: str | None) -> OpenApiArchive | None:
    if reason is None:
        return None
    return OpenApiArchive(reason=reason)


def to_openapi_restore(reason: str | None) -> OpenApiRestore | None:
    if reason is None:
        return None
    return OpenApiRestore(reason=reason)


def to_openapi_id(
    value: Managed | UUID | str,
    managed_type: type[Managed] = Managed,
    strict: bool = True,
) -> str:
    if isinstance(value, Managed):
        if not strict or isinstance(value, managed_type):
            return str(value.id)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, str):
        return value
    if not strict:
        return str(value)

    raise TypeError(
        f"id parameter must be an instance of istari.{managed_type.__name__}, uuid.UUID, or str not {type(value)}: "
        f"'{value}'"
    )


def to_openapi_source_revision_id(
    id_source: ResourceLike | File | Revision | UUID | str,
) -> str:
    if isinstance(id_source, str):
        return id_source
    if isinstance(id_source, UUID):
        return str(id_source)
    if isinstance(id_source, Revision):
        return to_openapi_source_revision_id(id_source.id)
    if isinstance(id_source, File):
        return to_openapi_source_revision_id(id_source.revision)
    if isinstance(id_source, ResourceLike):
        return to_openapi_source_revision_id(id_source.file)
    raise TypeError(
        f"Invalid source -- must be an instance of Resource, File, Revision, UUID, or str (not "
        f"{type(id_source).__name__}) "
        f"to be converted to a openapi source id: '{id_source}' ({type(id_source)})"
    )


def to_openapi_id_or_none(
    value: Managed | UUID | str | None,
    managed_type: type[Managed] = Managed,
    strict: bool = True,
) -> str | None:
    return to_openapi_id(value, managed_type, strict) if value is not None else None


def to_new_source_list_or_none(
    source_inputs=Iterable[NewSource | ResourceLike | File | Revision | UUID | str]
    | None,
) -> list[NewSource] | None:
    if source_inputs is None:
        return None
    return [NewSource.from_source_input(source_input) for source_input in source_inputs]


@cache
def resource_type_map() -> dict[str, type["ResourceLike"]]:
    return {
        Artifact.__name__: Artifact,
        Comment.__name__: Comment,
        Model.__name__: Model,
        Job.__name__: Job,
    }


def to_resource_type(name: str) -> type["ResourceLike"] | None:
    if not name:
        return None
    return resource_type_map().get(name, None)
