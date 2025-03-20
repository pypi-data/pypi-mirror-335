from pathlib import Path
from .env import (
    env_cache_root,
    env_bool,
    env_int,
    env_str,
)
import logging
from dataclasses import field, dataclass
from functools import cached_property
import os
import istari_digital_core

from istari_digital_client import openapi_client

logger = logging.getLogger("istari-digital-client.configuration")


@dataclass(frozen=True)
class Configuration:
    registry_url: str | None = field(
        default_factory=env_str("ISTARI_REGISTRY_URL", default=None)
    )
    registry_auth_token: str | None = field(
        default_factory=env_str("ISTARI_REGISTRY_AUTH_TOKEN")
    )
    retry_enabled: bool | None = field(
        default_factory=env_bool("ISTARI_CLIENT_RETRY_ENABLED", default=True)
    )
    retry_max_attempts: int | None = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MAX_ATTEMPTS")
    )
    retry_min_interval_millis: int | None = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MIN_INTERVAL_MILLIS")
    )
    retry_max_interval_millis: int | None = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MAX_INTERVAL_MILLIS")
    )
    retry_jitter_enabled: bool | None = field(
        default_factory=env_bool("ISTARI_CLIENT_RETRY_JITTER_ENABLED", default=True)
    )
    filesystem_cache_enabled: bool | None = field(
        default_factory=env_bool("ISTARI_CLIENT_FILESYSTEM_CACHE_ENABLED", default=True)
    )
    filesystem_cache_root: Path = field(
        default_factory=env_cache_root("ISTARI_CLIENT_FILESYSTEM_CACHE_ROOT")
    )
    filesystem_cache_clean_on_exit: bool = field(
        default_factory=env_bool(
            "ISTARI_CLIENT_FILESYSTEM_CACHE_CLEAN_BEFORE_EXIT", default=True
        )
    )
    memory_cache_enabled: bool | None = field(
        default_factory=env_bool("ISTARI_CLIENT_MEMORY_CACHE_ENABLED", default=True)
    )
    memory_cache_max_items: int | None = field(
        default_factory=env_int("ISTARI_CLIENT_MEMORY_CACHE_MAX_ITEMS")
    )
    memory_cache_max_item_size: int | None = field(
        default_factory=env_int("ISTARI_CLIENT_MEMORY_CACHE_MAX_ITEM_SIZE")
    )

    def __post_init__(self) -> None:
        os.environ["ISTARI_REGISTRY_URL"] = self.registry_url or ""
        logger.debug(
            "set os.environ['ISTARI_REGISTRY_URL'] to '%s'",
            os.environ.get("ISTARI_REGISTRY_URL"),
        )
        os.environ["ISTARI_REGISTRY_AUTH_TOKEN"] = self.registry_auth_token or ""
        logger.debug(
            "setting os.environ['ISTARI_REGISTRY_AUTH_TOKEN'] to '%s'",
            os.environ.get("ISTARI_REGISTRY_AUTH_TOKEN"),
        )

    @classmethod
    def from_native_configuration(
        cls: type["Configuration"], native: istari_digital_core.Configuration
    ) -> "Configuration":
        return Configuration(
            registry_url=native.registry_url,
            registry_auth_token=native.registry_auth_token,
            retry_enabled=native.retry_enabled,  # type: ignore[attr-defined]
            retry_max_attempts=native.retry_max_attempts,  # type: ignore[attr-defined]
            retry_min_interval_millis=native.retry_min_interval_millis,  # type: ignore[attr-defined]
            retry_max_interval_millis=native.retry_max_interval_millis,  # type: ignore[attr-defined]
            retry_jitter_enabled=native.retry_jitter_enabled,
        )

    @cached_property
    def native_configuration(self) -> istari_digital_core.Configuration:
        return istari_digital_core.Configuration(
            registry_url=self.registry_url,
            registry_auth_token=self.registry_auth_token,
            retry_enabled=self.retry_enabled,  # type: ignore[attr-defined]
            retry_max_attempts=self.retry_max_attempts,  # type: ignore[attr-defined]
            retry_min_interval_millis=self.retry_min_interval_millis,  # type: ignore[attr-defined]
            retry_max_interval_millis=self.retry_max_interval_millis,  # type: ignore[attr-defined]
            retry_jitter_enabled=self.retry_jitter_enabled,
        )

    @cached_property
    def openapi_client_configuration(self) -> openapi_client.Configuration:
        return openapi_client.Configuration(
            host=self.registry_url,
            access_token=self.registry_auth_token,
            retries=self.retry_max_attempts,
        )


class ConfigurationError(ValueError):
    pass
