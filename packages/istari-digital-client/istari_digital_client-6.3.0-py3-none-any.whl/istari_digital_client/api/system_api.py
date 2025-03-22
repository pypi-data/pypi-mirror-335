import typing
from typing import Optional
from uuid import UUID

from pydantic import StrictStr
from istari_digital_client.configuration import Configuration
from istari_digital_client.models import to_openapi_archive, to_openapi_restore
from istari_digital_client.openapi_client.api_client import ApiClient
from istari_digital_client.openapi_client.api.systems_api import (
    SystemsApi as OpenApiSystemApi,
)

from istari_digital_client.openapi_client.models.new_system import NewSystem
from istari_digital_client.openapi_client.models.system import System
from istari_digital_client.openapi_client.models.update_system import UpdateSystem
from istari_digital_client.openapi_client.models.page_system import PageSystem
from istari_digital_client.openapi_client.models.system_baseline import SystemBaseline
from istari_digital_client.openapi_client.models.new_system_configuration import (
    NewSystemConfiguration,
)
from istari_digital_client.openapi_client.models.page_tracked_file import (
    PageTrackedFile,
)
from istari_digital_client.openapi_client.models.system_configuration import (
    SystemConfiguration,
)
from istari_digital_client.openapi_client.models.page_system_configuration import (
    PageSystemConfiguration,
)
from istari_digital_client.openapi_client.models.snapshot import Snapshot
from istari_digital_client.openapi_client.models.new_snapshot import NewSnapshot
from istari_digital_client.openapi_client.models.response_create_snapshot import (
    ResponseCreateSnapshot,
)
from istari_digital_client.openapi_client.models.page_snapshot import PageSnapshot
from istari_digital_client.openapi_client.models.page_snapshot_item import (
    PageSnapshotItem,
)
from istari_digital_client.openapi_client.models.snapshot_tag import SnapshotTag
from istari_digital_client.openapi_client.models.new_snapshot_tag import NewSnapshotTag
from istari_digital_client.openapi_client.models.page_snapshot_tag import (
    PageSnapshotTag,
)
from istari_digital_client.openapi_client.models.update_tag import UpdateTag
from istari_digital_client.openapi_client.models.archive_status import ArchiveStatus

if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client


class SystemApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_system_api = OpenApiSystemApi(api_client)
        self.client = client

    def get_system_baseline(self, system_id: UUID) -> SystemBaseline:
        return self.openapi_system_api.get_system_baseline(str(system_id))

    def get_system(self, system_id: UUID) -> System:
        """Get a system by its ID."""
        return self.openapi_system_api.get_system(str(system_id))

    def create_system(self, new_system: NewSystem) -> System:
        return self.openapi_system_api.create_system(new_system)

    def update_system(self, system_id: UUID, update_system: UpdateSystem) -> System:
        return self.openapi_system_api.update_system(str(system_id), update_system)

    def get_configuration(self, configuration_id: UUID) -> SystemConfiguration:
        """Get a configuration by its ID."""
        return self.openapi_system_api.get_configuration(str(configuration_id))

    def create_configuration(
        self,
        system_id: UUID,
        new_configuration: NewSystemConfiguration,
    ) -> SystemConfiguration:
        return self.openapi_system_api.create_configuration(
            str(system_id), new_configuration
        )

    def get_snapshot(self, snapshot_id: UUID) -> Snapshot:
        """Get a snapshot by its ID."""
        return self.openapi_system_api.get_snapshot(str(snapshot_id))

    def create_snapshot(
        self,
        configuration_id: UUID,
        new_snapshot: NewSnapshot,
    ) -> ResponseCreateSnapshot:
        return self.openapi_system_api.create_snapshot(
            str(configuration_id), new_snapshot
        )

    def get_tag(self, tag_id: UUID) -> SnapshotTag:
        """Get a tag by its ID."""
        return self.openapi_system_api.get_tag(str(tag_id))

    def create_tag(self, snapshot_id: UUID, new_tag: NewSnapshotTag) -> SnapshotTag:
        return self.openapi_system_api.create_tag(str(snapshot_id), new_tag)

    def update_tag(self, tag_id: UUID, update_tag: UpdateTag) -> SnapshotTag:
        """Updates a tag by its ID with a new snapshot_id."""
        return self.openapi_system_api.update_tag(str(tag_id), update_tag)

    def list_systems(
        self,
        archive_status: Optional[ArchiveStatus] = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSystem:
        return self.openapi_system_api.list_systems(page, size, archive_status, sort)

    def list_configurations(
        self,
        system_id: UUID,
        archive_status: ArchiveStatus | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSystemConfiguration:
        return self.openapi_system_api.list_system_configurations(
            str(system_id), page, size, archive_status, sort
        )

    def list_tracked_files(
        self,
        configuration_id: UUID,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageTrackedFile:
        """Lists tracked files for a system or configuration."""
        return self.openapi_system_api.list_tracked_files(
            configuration_id=str(configuration_id),
            page=page,
            size=size,
            sort=sort,
        )

    def list_snapshots(
        self,
        system_id: UUID | None = None,
        configuration_id: UUID | None = None,
        tag: StrictStr | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSnapshot:
        return self.openapi_system_api.list_snapshots(
            system_id=str(system_id) if system_id else None,
            configuration_id=str(configuration_id) if configuration_id else None,
            tag=tag,
            page=page,
            size=size,
            sort=sort,
        )

    def list_snapshot_items(
        self,
        snapshot_id: UUID,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> PageSnapshotItem:
        """Lists snapshot items for a given snapshot."""
        return self.openapi_system_api.list_snapshot_items(
            snapshot_id=str(snapshot_id), page=page, size=size, sort=sort
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
        return self.openapi_system_api.list_tags(
            system_id=str(system_id) if system_id else None,
            configuration_id=str(configuration_id) if configuration_id else None,
            snapshot_id=str(snapshot_id) if snapshot_id else None,
            archive_status=archive_status,
            page=page,
            size=size,
            sort=sort,
        )

    def archive_system(self, system_id: UUID, reason: str | None = None) -> System:
        """Archives a system by its ID with an optional reason."""
        return self.openapi_system_api.archive_system(
            str(system_id), to_openapi_archive(reason)
        )

    def restore_system(self, system_id: UUID, reason: str | None = None) -> System:
        """Restores an archived system by its ID with an optional reason."""
        return self.openapi_system_api.restore_system(
            str(system_id), to_openapi_restore(reason)
        )

    def archive_configuration(
        self, configuration_id: UUID, reason: str | None = None
    ) -> SystemConfiguration:
        """Archives a system configuration by its ID with an optional reason."""
        return self.openapi_system_api.archive_configuration(
            str(configuration_id), to_openapi_archive(reason)
        )

    def restore_configuration(
        self, configuration_id: UUID, reason: str | None = None
    ) -> SystemConfiguration:
        """Restores an archived system configuration by its ID with an optional reason."""
        return self.openapi_system_api.restore_configuration(
            str(configuration_id), to_openapi_restore(reason)
        )

    def archive_tag(self, tag_id: UUID) -> SnapshotTag:
        """Archives a tag by its ID with an optional reason."""
        return self.openapi_system_api.archive_tag(str(tag_id))

    def restore_tag(self, tag_id: UUID) -> SnapshotTag:
        """Restores an archived tag by its ID with an optional reason."""
        return self.openapi_system_api.restore_tag(str(tag_id))
