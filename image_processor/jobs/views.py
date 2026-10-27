from rest_framework import generics

from .models import ProcessingJob
from .serializers import ProcessingJobSerializer


class JobCreateView(generics.CreateAPIView):
    queryset = ProcessingJob.objects.all()
    serializer_class = ProcessingJobSerializer


class JobDetailView(generics.RetrieveAPIView):
    queryset = ProcessingJob.objects.all()
    serializer_class = ProcessingJobSerializer
