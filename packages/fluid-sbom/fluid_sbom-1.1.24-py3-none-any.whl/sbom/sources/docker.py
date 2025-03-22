import json
import logging
import os
import re
import shutil
import subprocess  # nosec
import tarfile
import tempfile
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from sbom.utils.file import extract_tar_file

LOGGER = logging.getLogger(__name__)


class LayerData(BaseModel):
    mimetype: str
    digest: str
    size: int
    annotations: dict[str, str] | None
    model_config = ConfigDict(frozen=True)


class ImageMetadata(BaseModel):
    name: str
    digest: str
    repotags: list[str]
    created: str
    dockerversion: str
    labels: dict[str, str] | None
    architecture: str
    os: str
    layers: list[str]
    layersdata: list[LayerData]
    env: list[str]
    image_ref: str = ""
    model_config = ConfigDict(frozen=True)


class LayerInfo(BaseModel):
    id_: str
    tar_full_path: str
    metadata: dict[str, Any]


class ImageContext(BaseModel):
    id: str
    name: str
    publisher: str | None
    arch: str
    size: str
    full_extraction_dir: str
    layers_dir: str
    manifest: dict[str, Any]
    image_ref: str

    def get_layer_info(self, layer_id: str) -> LayerInfo | None:
        if layer_metadata := next(x for x in self.manifest["layers"] if x["id"] == layer_id):
            return LayerInfo(
                id_=layer_id,
                tar_full_path=os.path.join(self.layers_dir, layer_metadata),
                metadata=layer_metadata,
            )
        return None


def custom_object_hook(json_object: dict[str, Any]) -> ImageMetadata | dict:
    if "Name" in json_object and "Digest" in json_object and "RepoTags" in json_object:
        layersdata = [
            LayerData(
                mimetype=layer_data["MIMEType"],
                digest=layer_data["Digest"],
                size=layer_data["Size"],
                annotations=layer_data.get("Annotations"),
            )
            for layer_data in json_object["LayersData"]
        ]
        return ImageMetadata(
            name=json_object["Name"],
            digest=json_object["Digest"],
            repotags=json_object["RepoTags"],
            created=json_object["Created"],
            dockerversion=json_object["DockerVersion"],
            labels=json_object["Labels"],
            architecture=json_object["Architecture"],
            os=json_object["Os"],
            layers=json_object["Layers"],
            layersdata=layersdata,
            env=json_object["Env"],
        )
    return json_object


def _extract_present_layers(
    layers_dir: str,
    output_dir: str,
) -> None:
    for file_path in sorted(os.listdir(layers_dir)):
        layer_tar_path = os.path.join(layers_dir, file_path, "layer.tar")
        if (
            Path(layer_tar_path).exists()
            and Path(layer_tar_path).is_file()
            and tarfile.is_tarfile(layer_tar_path)
        ):
            Path(os.path.join(output_dir, file_path)).mkdir(
                parents=True,
                exist_ok=True,
            )
            extract_tar_file(
                layer_tar_path,
                os.path.join(output_dir, file_path),
            )


def copy_image(  # noqa: PLR0913
    image_ref: str,
    dest_path: str,
    *,
    username: str | None = None,
    password: str | None = None,
    aws_creds: str | None = None,
    token: str | None = None,
) -> bool:
    skopeo_path = shutil.which("skopeo")
    formated_image_ref = format_image_ref(image_ref)
    if not skopeo_path or not formated_image_ref:
        return False
    command_args = [
        skopeo_path,
        "copy",
        "--dest-decompress",
        "--src-tls-verify=false",
        "--insecure-policy",
        "--override-os",
        "linux",
        formated_image_ref,
        f"dir:{dest_path}",
    ]
    if username and password:
        command_args.extend(
            ["--src-username", username, "--src-password", password],
        )
    elif token:
        command_args.extend(["--src-registry-token", token])
    elif aws_creds:
        command_args.append(f"--src-creds={aws_creds}")

    with subprocess.Popen(  # noqa: S603
        command_args,
        shell=False,
        stdout=subprocess.PIPE,
    ) as proc:
        exit_code = proc.wait()
        return exit_code == 0


def extract_docker_image(  # noqa: PLR0913
    image: ImageMetadata,
    output_dir: str,
    *,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> tuple[str, dict[str, Any]]:
    layers_dir_temp = tempfile.mkdtemp()
    copy_image(
        format_image_ref(image.image_ref, daemon=daemon) or image.image_ref,
        layers_dir_temp,
        username=username,
        password=password,
        token=token,
        aws_creds=aws_creds,
    )
    with Path(os.path.join(layers_dir_temp, "manifest.json")).open(
        encoding="utf-8",
    ) as json_reader:
        manifest = json.load(json_reader)
    with Path(
        os.path.join(
            layers_dir_temp,
            manifest["config"]["digest"].replace("sha256:", ""),
        ),
    ).open(
        encoding="utf-8",
    ) as json_reader:
        manifest["config_full"] = json.load(json_reader)

    for layer in manifest["layers"]:
        layer_digest = layer["digest"].replace("sha256:", "")
        layer_tar_path = os.path.join(
            layers_dir_temp,
            layer_digest,
        )
        if Path(layer_tar_path).exists():
            Path(os.path.join(output_dir, layer["digest"])).mkdir(
                parents=True,
                exist_ok=True,
            )
            extract_tar_file(
                layer_tar_path,
                os.path.join(output_dir, layer["digest"]),
            )

    return layers_dir_temp, manifest


def format_image_ref(image_ref: str, *, daemon: bool = False) -> str | None:
    image_ref_pattern = (
        r"^(?:(?P<host>[\w\.\-]+(?:\:\d+)?)/)?"
        r"(?P<namespace>(?:[\w\.\-]+(?:/[\w\.\-]+)*)?/)?"
        r"(?P<image>[\w\.\-]+)(?::(?P<tag>[\w\.\-]+))?(?:@"
        r"(?P<digest>sha256:[A-Fa-f0-9]{64}))?$"
    )
    prefix_to_use = "docker-daemon:" if daemon else "docker://"
    prefix_used: str | None = None
    prefixes = ["docker://", "docker-daemon:"]
    for prefix in prefixes:
        if image_ref.startswith(prefix):
            image_ref = image_ref.replace(prefix, "", 1)
            prefix_used = prefix
            break

    prefix_to_use = prefix_used or prefix_to_use

    if re.match(image_ref_pattern, image_ref):
        return f"{prefix_to_use}{image_ref}"

    LOGGER.error("Invalid image reference: %s", image_ref_pattern)
    return None


def get_docker_image(  # noqa: PLR0913
    image_ref: str,
    *,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> ImageMetadata | None:
    skopeo_path = shutil.which("skopeo")
    formated_image_ref = format_image_ref(image_ref, daemon=daemon)
    if not skopeo_path or not formated_image_ref:
        return None
    command_args = [
        skopeo_path,
        "inspect",
        "--tls-verify=false",
        "--override-os",
        "linux",
        formated_image_ref,
    ]

    if username and password:
        command_args.extend(["--username", username, "--password", password])

    elif token:
        command_args.append(f"--registry-token={token}")

    elif aws_creds:
        command_args.append(f"--creds={aws_creds}")

    try:
        result = subprocess.run(  # noqa: S603
            command_args,
            check=True,
            capture_output=True,
            text=True,
        )

        image_metadata: ImageMetadata = json.loads(
            result.stdout,
            object_hook=custom_object_hook,
        )
        if image_metadata:
            image_metadata = image_metadata.model_copy(
                update={"image_ref": image_ref},
            )

        return image_metadata
    except subprocess.CalledProcessError as error:
        error_message = f"An error occurred: {error.stderr.strip()}"
        LOGGER.exception(error_message)
        return None


def get_image_context(  # noqa: PLR0913
    *,
    image: ImageMetadata,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> ImageContext | None:
    temp_dir = tempfile.mkdtemp()
    layers_dir, manifest = extract_docker_image(
        image,
        temp_dir,
        username=username,
        password=password,
        token=token,
        aws_creds=aws_creds,
        daemon=daemon,
    )

    return ImageContext(
        id=image.digest,
        name=image.name,
        publisher="",
        arch=image.architecture,
        size=str(sum(x.size for x in image.layersdata)),
        full_extraction_dir=temp_dir,
        layers_dir=layers_dir,
        manifest=manifest,
        image_ref=image.image_ref,
    )
