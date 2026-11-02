from typing import Optional

from rest_framework import serializers

from .models import Conversation, Message
from .services import unread_messages


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_username",
            "text",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "conversation", "sender", "is_read", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    candidate_username = serializers.CharField(source="candidate.username", read_only=True)
    offer_title = serializers.CharField(source="offer.title", read_only=True)
    organization_name = serializers.CharField(source="offer.organization.name", read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "offer",
            "offer_title",
            "organization_name",
            "candidate",
            "candidate_username",
            "created_at",
            "updated_at",
            "last_message",
            "unread_count",
        ]
        read_only_fields = fields

    def get_last_message(self, obj) -> Optional[str]:
        last = obj.messages.last()
        return last.text if last else None

    def get_unread_count(self, obj) -> int:
        return unread_messages(obj, self.context["request"].user).count()


class StartConversationSerializer(serializers.Serializer):
    offer = serializers.IntegerField()
    candidate = serializers.IntegerField(required=False)


class SendMessageInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000)