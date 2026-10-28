from rest_framework import generics

from .models import ProcessingJob
from .serializers import ProcessingJobSerializer


class JobCreateView(generics.CreateAPIView):
    """ Create jobs for an authenticated project. """
    serializer_class = ProcessingJobSerializer

    def perform_create(self, serializer):
        serializer.save(
            project=self.request.user.username
        )


class JobDetailView(generics.RetrieveAPIView):
    """ Retrieve jobs that belong to an authenticated project. """
    serializer_class = ProcessingJobSerializer

    def get_queryset(self):
        return ProcessingJob.objects.filter(
            project=self.request.user.username
        )
