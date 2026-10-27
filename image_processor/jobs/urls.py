from django.urls import path

from .views import JobCreateView, JobDetailView

urlpatterns = [
    path("jobs/", JobCreateView.as_view(), name="job-create"),
    path("jobs/<uuid:pk>/", JobDetailView.as_view(), name="job-detail"),
]
