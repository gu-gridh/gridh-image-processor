from types import SimpleNamespace

from rest_framework import serializers

from .models import ProcessingJob
from .services.paths import (
    InvalidJobPath,
    resolve_job_paths,
)


class ProcessingJobSerializer(serializers.ModelSerializer):
    """
    Serializer for all fields. Uses the validation from the service to check
    the file paths of original and target images.

    Returns:
    dict: Validated serializer attributes.

    Raises:
    serializers.ValidationError: If project, job type, original or target path
                                 is invalid.
    """

    class Meta:
        model = ProcessingJob

        fields = "__all__"

        read_only_fields = (
            "id",
            "status",
            "error_message",
            "created_at",
            "started_at",
            "finished_at",
        )

    def validate(self, attrs):
        job = SimpleNamespace(**attrs)

        try:
            resolve_job_paths(job)
        except InvalidJobPath as exc:
            raise serializers.ValidationError(
                {"path": str(exc)}
            )

        return attrs
