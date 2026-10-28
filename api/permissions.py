from rest_framework.permissions import SAFE_METHODS, BasePermission

from organizations.models import Membership


def is_member(user, organization):
    return user.is_staff or Membership.objects.filter(
        user=user,
        organization=organization,
    ).exists()


class IsOrganizationMemberOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return is_member(request.user, obj.organization)