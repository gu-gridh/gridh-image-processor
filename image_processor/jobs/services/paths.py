from pathlib import Path

from django.conf import settings


class InvalidJobPath(ValueError):
    """Raised for invalid or unauthorized job paths."""


def resolve_job_paths(job):
    """
    Resolve and validate original and target paths. Also used in serializer.

    Expected directory structure:
    <project>/
    ├── original/
    |   ├── panorama/
    |   └── iiif/
    ├── panorama/
    └── iiif/

    Returns:
        tuple[Path, Path]: Resolved source and destination paths.

    Raises:
        InvalidJobPath: If the project, job type, or paths are invalid.
    """

    # Before doing anything, check if project exists
    project_config = settings.PROJECTS.get(job.project)

    if project_config is None:
        raise InvalidJobPath(f"Unknown project: {job.project}")

    # Check job type
    # TODO: Change me for IIIF - Test only panorama for now
    allowed_jobs = project_config.get("allowed_jobs", ["panorama"])

    if job.job_type not in allowed_jobs:
        raise InvalidJobPath(
            f"Job type {job.job_type} not allowed for project {job.project}")

    # Find project storage root
    root = Path(project_config["storage_root"]).resolve(strict=True)

    if not root.is_dir():
        raise InvalidJobPath("Project storage root is not a directory")

    original = Path(job.original)
    original_root = (root / "original" / job.job_type).resolve()
    original_path = (root / original).resolve()

    target = Path(job.target)
    target_root = (root / job.job_type).resolve()
    target_path = (root / target).resolve()

    # validate relative paths
    for path in (original, target):
        if path.is_absolute():
            raise InvalidJobPath("Path must be relative")
        if not path.parts or ".." in path.parts:
            raise InvalidJobPath("Invalid relative path")

    if not original_path.is_relative_to(original_root):
        raise InvalidJobPath("Original must be inside "
                             "original/{job.job_type}/ folder.")

    if not target_path.is_relative_to(target_root):
        raise InvalidJobPath("Target must be inside {job.job_type}/ "
                             "folder.")

    if not original_path.is_file():
        raise InvalidJobPath("Original image does not exist")

    if not target_path.is_relative_to(root):
        raise InvalidJobPath("Target outside project storage")
    if target_path.exists() and not target_path.is_dir():
        raise InvalidJobPath("Target must be a directory")

    return original_path, target_path
