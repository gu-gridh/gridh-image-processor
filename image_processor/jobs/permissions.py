from django.conf import settings
from rest_framework.permissions import BasePermission


class IsConfiguredProject(BasePermission):
    """
    Only authenticated users are allowed access to the image processor.
    The user has to be added to the image processor database.
    The username has to match the project name in projects_config.json.

    Returns:
        bool: True if the user belongs to an allowed project.
    """

    message = "Project is not authorized to use this service."

    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and user.is_active
            and user.username in settings.PROJECTS
        )
