import typing
from uuid import UUID

from istari_digital_client.configuration import Configuration
from istari_digital_client.models import AccessRelationship
from istari_digital_client.models import AccessRelation
from istari_digital_client.models import Artifact
from istari_digital_client.models import Function
from istari_digital_client.models import Model
from istari_digital_client.models import Job
from istari_digital_client.models import to_openapi_id
from istari_digital_client.openapi_client.api.access_api import (
    AccessApi as OpenApiAccessApi,
)
from istari_digital_client.openapi_client.models.update_access_relationship import (
    UpdateAccessRelationship,
)
from istari_digital_client.openapi_client.api_client import ApiClient
from istari_digital_client.openapi_client.models.patch_op import PatchOp
from istari_digital_client.openapi_client.models.access_resource_type import (
    AccessResourceType,
)
from istari_digital_client.openapi_client.models.access_subject_type import (
    AccessSubjectType,
)

if typing.TYPE_CHECKING:
    from istari_digital_client import Client


class AccessApi:
    def __init__(
        self,
        config: Configuration,
        client: "Client",
    ) -> None:
        api_client = ApiClient(config.openapi_client_configuration)
        self.openapi_access_api = OpenApiAccessApi(api_client)
        self.client = client

    def list_artifact_access(
        self,
        artifact_id: str | UUID | Artifact,
    ) -> list[AccessRelationship]:
        artifact_id = to_openapi_id(artifact_id, Artifact)
        openapi_access_relationships = self.openapi_access_api.list_artifact_access(
            artifact_id
        )
        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def list_job_access(
        self,
        job_id: str | UUID | Job,
    ) -> list[AccessRelationship]:
        job_id = to_openapi_id(job_id, Job)
        openapi_access_relationships = self.openapi_access_api.list_job_access(job_id)

        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def list_model_access(
        self,
        model_id: UUID | str | Model,  # noqa: F821
    ) -> list[AccessRelationship]:
        model_id = to_openapi_id(model_id, Model)
        openapi_access_relationships = self.openapi_access_api.list_model_access(
            model_id
        )

        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def list_function_access(
        self,
        function_id: UUID | str | Function,  # noqa: F821
    ) -> list[AccessRelationship]:
        function_id = to_openapi_id(function_id, Function)
        openapi_access_relationships = self.openapi_access_api.list_function_access(
            function_id
        )

        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def patch_artifact_access(
        self,
        artifact_id: str | UUID | Artifact,
        relationship: AccessRelationship,
        patch_op: PatchOp | None = None,
    ) -> list[AccessRelationship]:
        artifact_id = to_openapi_id(artifact_id, Artifact)
        openapi_access_relationships = self.openapi_access_api.patch_artifact_access(
            artifact_id,
            relationship.inner,
            patch_op=patch_op,
        )

        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def patch_job_access(
        self,
        job_id: str | UUID | Job,
        relationship: AccessRelationship,
        patch_op: PatchOp | None = None,
    ) -> list[AccessRelationship]:
        job_id = to_openapi_id(job_id, Job)
        openapi_access_relationships = self.openapi_access_api.patch_job_access(
            job_id,
            relationship.inner,
            patch_op=patch_op,
        )

        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def patch_model_access(
        self,
        model_id: UUID | str | Model,
        relationship: AccessRelationship,
        patch_op: PatchOp | None = None,
    ) -> list[AccessRelationship]:
        model_id = to_openapi_id(model_id, Model)
        openapi_access_relationships = self.openapi_access_api.patch_model_access(
            model_id,
            relationship.inner,
            patch_op=patch_op,
        )

        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def patch_function_access(
        self,
        function_id: UUID | str | Function,
        relationship: AccessRelationship,
        patch_op: PatchOp | None = None,
    ) -> list[AccessRelationship]:
        function_id = to_openapi_id(function_id, Function)
        openapi_access_relationships = self.openapi_access_api.patch_function_access(
            function_id,
            relationship.inner,
            patch_op=patch_op,
        )

        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def create_access(
        self,
        access_relationship: AccessRelationship,
    ) -> AccessRelationship:
        openapi_access_relationship = self.openapi_access_api.create_access(
            access_relationship.inner
        )

        return AccessRelationship(
            openapi_access_relationship.subject_type,
            openapi_access_relationship.subject_id,
            openapi_access_relationship.relation,
            openapi_access_relationship.resource_type,
            openapi_access_relationship.resource_id,
        )

    def list_access(
        self,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
    ) -> list[AccessRelationship]:
        if isinstance(resource_id, UUID):
            resource_id = str(resource_id)

        openapi_access_relationships = self.openapi_access_api.list_access(
            resource_type, resource_id
        )

        return [
            AccessRelationship(
                ar.subject_type,
                ar.subject_id,
                ar.relation,
                ar.resource_type,
                ar.resource_id,
            )
            for ar in openapi_access_relationships
        ]

    def update_access(
        self,
        subject_type: AccessSubjectType,
        subject_id: UUID | str,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
        update_access_relationship: UpdateAccessRelationship,
    ) -> AccessRelationship:
        if isinstance(subject_id, UUID):
            subject_id = str(subject_id)
        if isinstance(resource_id, UUID):
            resource_id = str(resource_id)

        openapi_access_relationship = self.openapi_access_api.update_access(
            subject_type,
            subject_id,
            resource_type,
            resource_id,
            update_access_relationship,
        )

        return AccessRelationship(
            openapi_access_relationship.subject_type,
            openapi_access_relationship.subject_id,
            openapi_access_relationship.relation,
            openapi_access_relationship.resource_type,
            openapi_access_relationship.resource_id,
        )

    def remove_access(
        self,
        subject_type: AccessSubjectType,
        subject_id: UUID | str,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
    ) -> None:
        if isinstance(subject_id, UUID):
            subject_id = str(subject_id)
        if isinstance(resource_id, UUID):
            resource_id = str(resource_id)

        self.openapi_access_api.remove_access(
            subject_type,
            subject_id,
            resource_type,
            resource_id,
        )

    def create_access_by_email_for_other_tenants(
        self,
        subject_type: AccessSubjectType,
        email: str,
        resource_type: AccessResourceType,
        resource_id: UUID | str,
        access_relationship: AccessRelation,
    ) -> AccessRelationship:
        if isinstance(resource_id, UUID):
            resource_id = str(resource_id)

        openapi_access_relationship = (
            self.openapi_access_api.create_access_by_email_for_other_tenants(
                subject_type,
                email,
                resource_type,
                resource_id,
                access_relationship,
            )
        )

        return AccessRelationship(
            openapi_access_relationship.subject_type,
            openapi_access_relationship.subject_id,
            openapi_access_relationship.relation,
            openapi_access_relationship.resource_type,
            openapi_access_relationship.resource_id,
        )
