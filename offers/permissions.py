from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.models import User


class IsRecruiterOrReadOnly(BasePermission):
    # """
    # Lectura para cualquiera.
    # Escritura solo para recruiters.
    # """

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and request.user.role == User.Role.RECRUITER
        )