import asyncio

from sbom.internal.file_resolver.container_image import ContainerImage
from sbom.model.core import SbomConfig, SourceType
from sbom.sources.directory_source import Directory
from sbom.sources.docker import get_docker_image, get_image_context
from sbom.sources.ecr import AwsRole, ecr_connection
from sbom.utils.exceptions import UnexpectedSBOMSourceError


def resolve_sbom_source(sbom_config: SbomConfig) -> Directory | ContainerImage:
    match sbom_config.source_type:
        case SourceType.DIRECTORY:
            return Directory(
                root=sbom_config.source,
                exclude=sbom_config.exclude,
            )
        case SourceType.DOCKER | SourceType.DOCKER_DAEMON:
            daemon = sbom_config.source_type == SourceType.DOCKER_DAEMON
            docker_image = get_docker_image(
                sbom_config.source,
                username=sbom_config.docker_user,
                password=sbom_config.docker_password,
                daemon=daemon,
            )
            if not docker_image:
                error_msg = f"No image found for {sbom_config.source}"
                raise ValueError(error_msg)

            context = get_image_context(
                image=docker_image,
                username=sbom_config.docker_user,
                password=sbom_config.docker_password,
                daemon=daemon,
            )
            if context is None:
                error_msg = f"No context found for {docker_image}"
                raise ValueError(error_msg)
            return ContainerImage(
                img=docker_image,
                context=context,
                lazy=False,
            )
        case SourceType.ECR:
            if not sbom_config.aws_role:
                error_msg = "The AWS role wasn't defined"
                raise ValueError(error_msg)
            role = AwsRole(
                external_id=sbom_config.aws_external_id,
                role=sbom_config.aws_role,
            )

            token, image_metadata = asyncio.run(
                ecr_connection(role, sbom_config.source),
            )

            if not image_metadata:
                error_msg = f"No image found for {sbom_config.source}"
                raise ValueError(error_msg)

            context = get_image_context(
                image=image_metadata,
                aws_creds=f"AWS:{token}",
            )
            if context is None:
                error_msg = f"No context found for {image_metadata}"
                raise ValueError(error_msg)
            return ContainerImage(
                img=image_metadata,
                context=context,
                lazy=False,
            )
        case _:
            raise UnexpectedSBOMSourceError
