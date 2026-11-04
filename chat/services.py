from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q

from candidates.models import Candidate
from offers.models import Offer, StatusChoices
from organizations.models import Membership

from .models import Conversation, Message

User = get_user_model()


def is_org_member(user, organization):
    return Membership.objects.filter(user=user, organization=organization).exists()


def is_participant(user, conversation):
    return user == conversation.candidate or is_org_member(
        user, conversation.offer.organization
    )


def conversations_for(user):
    organizations = Membership.objects.filter(user=user).values("organization")
    return Conversation.objects.filter(
        Q(candidate=user) | Q(offer__organization__in=organizations)
    )


def unread_messages(conversation, user):
    messages = conversation.messages.filter(is_read=False)
    if user == conversation.candidate:
        return messages.exclude(sender=user)
    return messages.filter(sender=conversation.candidate)


@transaction.atomic
def get_or_create_conversation(user, offer_id, candidate_id=None):
    offer = Offer.objects.select_for_update().get(pk=offer_id)

    if offer.status != StatusChoices.PUBLICADA:
        raise ValidationError("No se puede iniciar una conversación sobre esta oferta.")

    if candidate_id is None:
        if is_org_member(user, offer.organization):
            raise ValidationError(
                "No puedes iniciar una conversación sobre una oferta de tu organización."
            )
        candidate = user
    else:
        if not is_org_member(user, offer.organization):
            raise PermissionDenied("No perteneces a la organización de esta oferta.")
        candidate = User.objects.get(pk=candidate_id)
        profile = Candidate.objects.filter(user=candidate).first()
        if profile is None or not profile.allows_contact:
            raise ValidationError("Este candidato no acepta contacto.")

    return Conversation.objects.get_or_create(offer=offer, candidate=candidate)


@transaction.atomic
def send_message(user, conversation_id, text):
    clean_text = text.strip()
    if not clean_text:
        raise ValidationError("El mensaje no puede estar vacío.")
    if len(clean_text) > 1000:
        raise ValidationError("El mensaje no puede superar los 1000 caracteres.")

    conversation = (
        Conversation.objects.select_for_update()
        .select_related("offer__organization")
        .get(pk=conversation_id)
    )

    if not is_participant(user, conversation):
        raise PermissionDenied("No tienes permiso para enviar mensajes en esta conversación.")

    message = Message.objects.create(
        conversation=conversation,
        sender=user,
        text=clean_text,
    )
    conversation.save(update_fields=["updated_at"])
    return message


@transaction.atomic
def mark_messages_as_read(conversation_id, user):
    conversation = Conversation.objects.select_related("offer__organization").get(
        pk=conversation_id
    )

    if not is_participant(user, conversation):
        raise PermissionDenied("No tienes acceso a esta conversación.")

    unread_messages(conversation, user).update(is_read=True)