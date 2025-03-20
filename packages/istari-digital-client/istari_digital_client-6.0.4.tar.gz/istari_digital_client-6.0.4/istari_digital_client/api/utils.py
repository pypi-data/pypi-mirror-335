from istari_digital_client.openapi_client.models.archive_status import ArchiveStatus


def archive_status_from_str(status: str) -> ArchiveStatus:
    if isinstance(status, str):
        if status not in ["archived", "active", "all"]:
            raise ValueError(
                "archive_status must be either 'archived', 'active', or 'all'"
            )
        return ArchiveStatus(status)
