import json
import tempfile
import typing
from pathlib import Path
from typing import Iterable
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.models import (
    Job,
    JobPage,
    Model,
    PathLike,
    ResourceLike,
    to_openapi_id,
    to_openapi_id_or_none,
    to_new_source_list_or_none,
    JSON,
    Revision,
    File,
    StatusName,
    NewSource,
)
from istari_digital_client.openapi_client import ApiClient
from istari_digital_client.openapi_client import JobApi as OpenApiJobApi

if typing.TYPE_CHECKING:
    from istari_digital_client import Client


class JobApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_job_api = OpenApiJobApi(api_client)
        self.client = client

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
    ) -> Job:
        parameters_file_is_temp = False
        if parameters_file and (parameters or kwargs):
            raise ValueError(
                "Can't combine a parameters file with explicit parameters or parameter kwargs"
            )
        if not parameters_file:
            if parameters and kwargs:
                raise ValueError(
                    "Can't combine explicit parameters with parameters kwargs"
                )
            parameters = parameters or kwargs
            parameters_file = Path(
                tempfile.NamedTemporaryFile(
                    prefix="parameters", suffix=".json", delete=False
                ).name
            )
            parameters_file.write_text(json.dumps(parameters, indent=4))
            parameters_file_is_temp = True
        parameters_file = Path(parameters_file)
        try:
            file_revision = self.client.storage.create_revision(
                file_path=str(parameters_file),
                sources=to_new_source_list_or_none(sources),
                display_name=display_name,
                description=description,
                version_name=version_name,
                external_identifier=external_identifier,
            )

            model_id = to_openapi_id(model_id, Model)

            openapi_job = self.openapi_job_api.create_model_job(
                model_id=model_id,
                function_name=function,
                file_revision=file_revision,
                tool_name=tool_name,
                tool_version=tool_version,
                operating_system=operating_system,
                agent_identifier=agent_identifier,
            )
        finally:
            if parameters_file_is_temp:
                if parameters_file.exists():
                    parameters_file.unlink(missing_ok=True)

        return Job(openapi_job, self.client)

    def get_job(self, job_id: UUID | str | Job) -> Job:
        job_id = to_openapi_id(job_id, Job)
        openapi_job = self.openapi_job_api.get_job(job_id)

        return Job(openapi_job, self.client)

    def list_jobs(
        self,
        model_id: Model | UUID | str | None = None,
        status_name: StatusName | None = None,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> JobPage:
        model_id = to_openapi_id_or_none(model_id, Model)

        openapi_page = self.openapi_job_api.list_jobs(
            model_id=model_id,
            status_name=status_name,
            page=page,
            size=size,
            sort=sort,
        )

        return JobPage(openapi_page, self.client)

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
    ) -> Job:
        file_revision = self.client.storage.create_revision(
            file_path=path,
            sources=to_new_source_list_or_none(sources),
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        job_id = to_openapi_id(job_id, Job)

        openapi_job = self.openapi_job_api.update_job(
            job_id=job_id,
            file_revision=file_revision,
        )

        return Job(openapi_job, self.client)

    def update_job_status(
        self,
        job_id: UUID | str | Job,
        status_name: StatusName,
        agent_identifier: str | None = None,
    ) -> Job:
        job_id = to_openapi_id(job_id, Job)

        openapi_job = self.openapi_job_api.update_job_status(
            job_id=job_id,
            status_name=status_name,
            agent_identifier=agent_identifier,
        )

        return Job(openapi_job, self.client)
