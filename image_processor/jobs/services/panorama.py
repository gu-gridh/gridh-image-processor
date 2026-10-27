import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings

from .paths import resolve_job_paths


def generate_panorama(job):
    """
    Generate Pannellum multiresolution tiles using Podman.
    """

    # validate paths
    original, target = resolve_job_paths(job)

    # do not overwrite existing panorama output
    if target.exists():
        raise FileExistsError(f"target already exists: {target}")

    # create temp output directory to not expose partially generated panorama
    target.parent.mkdir(parents=True, exist_ok=True)

    staging = Path(
        tempfile.mkdtemp(
            prefix=".panorama-",
            dir=target.parent,
        )
    )

    try:
        command = [
            "podman",
            "run",
            "--rm",
            # Preserve groups for RHEL
            "--group-add",
            "keep-groups",
            # Read-only original directory.
            "-v",
            f"{original.parent}:/input:ro",
            # Writable output directory.
            "-v",
            f"{staging}:/output",
            # choose correct image
            settings.PANORAMA_CONTAINER_IMAGE,
            "--output",
            "/output/generated",
            f"/input/{original.name}",
        ]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=settings.PANORAMA_TIMEOUT,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Podman failed (exit code {e.returncode}):\n"
                f"STDOUT:\n{e.stdout}\n"
                f"STDERR:\n{e.stderr}"
            ) from e

        # check generated config file for problems
        generated = staging / "generated"

        config_file = generated / "config.json"

        if not config_file.is_file():
            raise RuntimeError("Pannellum did not generate config.json")

        with config_file.open() as f:
            config = json.load(f)

        if "multiRes" not in config:
            raise RuntimeError("Invalid Pannellum configuration")

        # Publish completed output.
        generated.rename(target)

        return target / "config.json"

    # clean up staging area
    finally:
        if staging.exists():
            shutil.rmtree(staging)
