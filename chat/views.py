from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation
from .permissions import IsConversationParticipant
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    SendMessageInputSerializer,
    StartConversationSerializer,
)
from .services import (
    conversations_for,
    get_or_create_conversation,
    mark_messages_as_read,
    send_message,
)

User = get_user_model()


def error_response(error):
    code = (
        status.HTTP_403_FORBIDDEN
        if isinstance(error, DjangoPermissionDenied)
        else status.HTTP_400_BAD_REQUEST
    )
    message = error.messages[0] if hasattr(error, "messages") else str(error)
    return Response({"detail": message}, status=code)


class ConversationViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Conversation.objects.none()
        return conversations_for(self.request.user).select_related(
            "offer", "offer__organization", "candidate"
        ).prefetch_related("messages")

    def get_serializer_class(self):
        if self.action == "create":
            return StartConversationSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = StartConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversation, created = get_or_create_conversation(
                user=request.user,
                offer_id=serializer.validated_data["offer"],
                candidate_id=serializer.validated_data.get("candidate"),
            )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "La oferta o el candidato no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except (DjangoValidationError, DjangoPermissionDenied) as error:
            return error_response(error)

        data = ConversationSerializer(conversation, context={"request": request}).data
        return Response(
            data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        mark_messages_as_read(conversation_id=conversation.pk, user=request.user)
        messages = conversation.messages.select_related("sender").all()
        return Response(MessageSerializer(messages, many=True).data)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        conversation = self.get_object()
        serializer = SendMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            message = send_message(
                user=request.user,
                conversation_id=conversation.pk,
                text=serializer.validated_data["text"],
            )
        except (DjangoValidationError, DjangoPermissionDenied) as error:
            return error_response(error)

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)