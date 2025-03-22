import typing
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.openapi_client import ModuleApi as OpenApiModuleApi
from istari_digital_client.openapi_client import ApiClient
from istari_digital_client.openapi_client.models.deprecation_reason import (
    DeprecationReason,
)
from istari_digital_client.openapi_client.models.usability_status_params import (
    UsabilityStatusParams,
)

if typing.TYPE_CHECKING:
    from istari_digital_client.client import Client

from istari_digital_client.openapi_client.models import (
    NewModuleManifest,
    UserModelInputs,
)
from istari_digital_client.models import (
    Function,
    FunctionPage,
    FunctionSchema,
    Module,
    ModulePage,
    ModuleVersion,
    ModuleVersionPage,
    to_openapi_id,
)


class ModuleApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_module_api = OpenApiModuleApi(api_client)
        self.client = client

    def create_module(
        self,
        new_module_manifest: NewModuleManifest,
    ) -> Module:
        openapi_module = self.openapi_module_api.create_module(
            new_module_manifest=new_module_manifest,
        )

        return Module(openapi_module, self.client)

    def get_function(self, function_id: UUID | str | Function) -> Function:
        function_id = to_openapi_id(function_id, Function)
        openapi_function = self.openapi_module_api.get_function(function_id)

        return Function(openapi_function, self.client)

    def get_module(self, module_id: UUID | str | Module) -> Module:
        if isinstance(module_id, Module):
            module_id = str(module_id.id)
        if isinstance(module_id, UUID):
            module_id = str(module_id)
        if isinstance(module_id, str):
            module_id = module_id

        openapi_module = self.openapi_module_api.get_module(module_id)

        return Module(openapi_module, self.client)

    def get_module_version(
        self,
        module_version_id: UUID | str | ModuleVersion,
    ) -> ModuleVersion:
        if isinstance(module_version_id, ModuleVersion):
            module_version_id = str(module_version_id.id)
        if isinstance(module_version_id, UUID):
            module_version_id = str(module_version_id)
        if isinstance(module_version_id, str):
            module_version_id = module_version_id

        openapi_module_version = self.openapi_module_api.get_module_version(
            module_version_id
        )

        return ModuleVersion(openapi_module_version, self.client)

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
    ) -> FunctionPage:
        openapi_page = self.openapi_module_api.list_functions(
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

        return FunctionPage(openapi_page, self.client)

    def get_function_schema(self, *, function_schema_id) -> FunctionSchema:
        openapi_function_schema = self.openapi_module_api.get_function_schema(
            function_schema_id=function_schema_id
        )
        return FunctionSchema(openapi_function_schema, self.client)

    def list_modules(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> ModulePage:
        openapi_page = self.openapi_module_api.list_modules(
            page=page,
            size=size,
            sort=sort,
        )

        return ModulePage(openapi_page, self.client)

    def list_module_versions(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> ModuleVersionPage:
        openapi_page = self.openapi_module_api.list_module_versions(
            page=page,
            size=size,
            sort=sort,
        )

        return ModuleVersionPage(openapi_page, self.client)

    def deprecate_module(
        self,
        module_id: UUID | str | Module,
        reason: DeprecationReason,
    ) -> Module:
        module_id = to_openapi_id(module_id, Module)
        openapi_module = self.openapi_module_api.deprecate_module(
            module_id=module_id,
            deprecation_reason=reason,
        )

        return Module(openapi_module, self.client)

    def deprecate_module_version(
        self,
        module_version_id: UUID | str | ModuleVersion,
        reason: DeprecationReason,
    ) -> ModuleVersion:
        module_version_id = to_openapi_id(module_version_id, ModuleVersion)
        openapi_module_version = self.openapi_module_api.deprecate_module_version(
            module_version_id=module_version_id,
            deprecation_reason=reason,
        )

        return ModuleVersion(openapi_module_version, self.client)
