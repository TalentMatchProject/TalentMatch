from rest_framework.permissions import BasePermission

from .services import is_participant


class IsConversationParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return is_participant(request.user, obj)