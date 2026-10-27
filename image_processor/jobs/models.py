import uuid

from django.db import models


class JobType(models.TextChoices):
    """
    The type of the job used in the ProcessingJob class.
    Currently panorama and iiif image generation are possible.
    """
    PANORAMA = "panorama", "Panorama"
    IIIF = "iiif", "IIIF"


class Status(models.TextChoices):
    """
    The status of the job used in the ProcessingJob class.
    It can be waiting to start (pending), running right now (processing),
    or finished with 'completed' if successful or 'failed' if not.
    """
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class ProcessingJob(models.Model):
    """
    A processing job represents an image generation task to convert images
    to iiif or panorama images which can be added to a task queue that can
    be processed by a worker.
    The following fields need to be defined:
        project: which project the job belongs to
        original: the path of the original image
        target: the path of the converted image
        job_type: if it is a panorama or a iiif conversion task
    A job also gets a uuid, a creation date and a status as well as when
    a process starts and finishes and potential error messages.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    project = models.CharField(
        max_length=100
    )

    original = models.CharField(
        max_length=500
    )

    target = models.CharField(
        max_length=500
    )

    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    error_message = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.project}: {self.job_type} ({self.status})"
