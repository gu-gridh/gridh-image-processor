import logging

from django.db import transaction
from django.utils import timezone
from jobs.models import JobType, ProcessingJob, Status
from jobs.services.panorama import generate_panorama

logger = logging.getLogger(__name__)


def claim_next_job():
    """
    Claim one pending job from the queue atomically. Jobs are ordered
    by creation date. The job status is switched to processing.
    """

    with transaction.atomic():
        job = (
            ProcessingJob.objects
            .select_for_update(skip_locked=True)
            .filter(status=Status.PENDING)
            .order_by("created_at")
            .first()
        )

        if job is None:
            return None

        job.status = Status.PROCESSING
        job.started_at = timezone.now()

        job.save(
            update_fields=["status", "started_at"]
        )

        return job


def process_job(job):
    """
    Execute a processing job and update its status.
    In case of panorama generate a panorama image with pannellum.
    TODO: add IIIF
    """

    logger.info(
        "Processing job %s (%s)",
        job.id,
        job.job_type,
    )

    try:
        if job.job_type == JobType.PANORAMA:
            generate_panorama(job)

        else:
            raise ValueError(
                f"Unsupported job type: {job.job_type}"
            )

    except Exception as exc:
        logger.exception(
            "Job %s failed",
            job.id,
        )

        ProcessingJob.objects.filter(pk=job.pk).update(
            status=Status.FAILED,
            error_message=str(exc)[:2000],
            finished_at=timezone.now(),
        )

    else:
        ProcessingJob.objects.filter(pk=job.pk).update(
            status=Status.COMPLETED,
            error_message="",
            finished_at=timezone.now(),
        )

        logger.info(
            "Job %s completed",
            job.id,
        )
