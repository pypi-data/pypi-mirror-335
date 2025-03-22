import logging
from pathlib import Path
from typing import TypedDict, Unpack

import confuse

from sbom.model.core import SbomConfig, SbomOutputFormat, SourceType
from sbom.utils.exceptions import InvalidConfigFileError

LOGGER = logging.getLogger(__name__)


class ScanArgs(TypedDict):
    o_from: str
    output_format: str
    output: str
    docker_user: str | None
    docker_password: str | None
    aws_external_id: str | None
    aws_role: str | None
    config: bool
    debug: bool


def _build_config(config_path: str) -> confuse.Configuration:
    template = confuse.Configuration("sbom", read=False)
    template.set_file(config_path)
    template.read(user=False, defaults=False)
    return template.get(
        confuse.Template(
            {
                "source": confuse.String(),
                "source_type": confuse.String(),
                "execution_id": confuse.String(),
                "exclude": confuse.Sequence(confuse.String()),
                "docker_credentials": confuse.Optional(
                    confuse.Template(
                        {
                            "username": confuse.Optional(confuse.String()),
                            "password": confuse.Optional(confuse.String()),
                        },
                    ),
                ),
                "aws_credentials": confuse.Optional(
                    confuse.Template(
                        {
                            "external_id": confuse.Optional(confuse.String()),
                            "role": confuse.Optional(confuse.String()),
                        },
                    ),
                ),
                "output": confuse.Template(
                    {
                        "name": confuse.String(),
                        "format": confuse.OneOf(
                            [_format.value for _format in SbomOutputFormat],
                        ),
                    },
                ),
                "debug": confuse.OneOf([True, False]),
            },
        ),
    )


def load(config_path: str) -> SbomConfig:
    config = _build_config(config_path)
    config_docker = config.pop("docker_credentials", {})
    config_aws = config.pop("aws_credentials", {})

    try:
        output = config.pop("output", None)

        sbom_config = SbomConfig(
            source=config.pop("source", None),
            source_type=config.pop("source_type", "dir"),
            output_format=output["format"],
            output=output["name"],
            exclude=config.pop("exclude", None) or (),
            docker_user=config_docker.pop("username", None),
            docker_password=config_docker.pop("password", None),
            aws_external_id=config_aws.pop("external_id", None),
            aws_role=config_aws.pop("role", None),
            execution_id=config.pop("execution_id", None),
            debug=config.pop("debug", False),
        )

        if config:
            unrecognized_keys = ", ".join(config)
            msg = (
                f"Some keys were not recognized: {unrecognized_keys}."
                " The analysis will be performed only using the supported keys"
                " and defaults."
            )
            LOGGER.warning(msg)
    except KeyError as exc:
        error_msg = f"Key: {exc.args[0]} is required"
        raise confuse.ConfigError(error_msg) from exc

    return sbom_config


def build_sbom_config(arg: str, **kwargs: Unpack[ScanArgs]) -> SbomConfig:
    if kwargs["config"]:
        if Path(arg).is_file():
            if not arg.endswith((".yaml", ".yml")):
                error_msg = "The configuration file must be a YAML format"
                raise InvalidConfigFileError(error_msg)

            return load(arg)

        error_msg = f"The configuration file is not a valid file: {arg}"
        raise InvalidConfigFileError(error_msg)

    return SbomConfig(
        source=arg,
        source_type=SourceType.from_string(kwargs["o_from"]),
        execution_id=None,
        output_format=kwargs["output_format"],
        output=kwargs["output"],
        exclude=(),
        docker_user=kwargs["docker_user"],
        docker_password=kwargs["docker_password"],
        aws_external_id=kwargs["aws_external_id"],
        aws_role=kwargs["aws_role"],
        debug=False,
    )
