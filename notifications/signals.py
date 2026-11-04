import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from chat.models import Message
from offers.models import Offer, SavedOffer, StatusChoices
from organizations.models import Membership

from .models import NotificationType
from .tasks import create_notification_async

logger = logging.getLogger(__name__)

UNAVAILABLE_STATUSES = (
    StatusChoices.PAUSADA,
    StatusChoices.CERRADA,
    StatusChoices.CUBIERTA,
)


def enqueue(**kwargs):
    try:
        create_notification_async.delay(**kwargs)
    except Exception:
        logger.exception("No se pudo encolar la notificación")


def organization_member_ids(organization, exclude_user_id=None):
    members = Membership.objects.filter(organization=organization)
    if exclude_user_id is not None:
        members = members.exclude(user_id=exclude_user_id)
    return list(members.values_list("user_id", flat=True))


@receiver(post_save, sender=Message)
def notify_new_chat_message(sender, instance, created, **kwargs):
    if not created:
        return

    conversation = instance.conversation
    if instance.sender_id == conversation.candidate_id:
        recipients = organization_member_ids(
            conversation.offer.organization, exclude_user_id=instance.sender_id
        )
    else:
        recipients = [conversation.candidate_id]

    preview = instance.text[:50] + ("..." if len(instance.text) > 50 else "")
    for recipient_id in recipients:
        enqueue(
            recipient_id=recipient_id,
            notification_type=NotificationType.NEW_MESSAGE,
            title="Nuevo mensaje recibido",
            body=f"{instance.sender.username}: {preview}",
            link=f"/api/v1/conversations/{conversation.pk}/messages/",
        )


@receiver(post_save, sender=SavedOffer)
def notify_offer_saved(sender, instance, created, **kwargs):
    if not created:
        return

    offer = instance.offer
    for recipient_id in organization_member_ids(offer.organization):
        enqueue(
            recipient_id=recipient_id,
            notification_type=NotificationType.OFFER_SAVED,
            title="Han guardado tu oferta",
            body=f"{instance.user.username} ha guardado la oferta '{offer.title}'.",
            link=f"/api/v1/offers/{offer.pk}/",
        )


@receiver(pre_save, sender=Offer)
def remember_previous_status(sender, instance, **kwargs):
    instance._previous_status = (
        Offer.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        if instance.pk
        else None
    )


@receiver(post_save, sender=Offer)
def notify_offer_unavailable(sender, instance, created, **kwargs):
    previous = getattr(instance, "_previous_status", None)
    if created or previous == instance.status:
        return
    if instance.status not in UNAVAILABLE_STATUSES:
        return

    for saved in SavedOffer.objects.filter(offer=instance).values_list("user_id", flat=True):
        enqueue(
            recipient_id=saved,
            notification_type=NotificationType.OFFER_UNAVAILABLE,
            title="Una oferta que guardaste ya no está disponible",
            body=f"La oferta '{instance.title}' ahora está {instance.get_status_display().lower()}.",
            link=f"/api/v1/offers/{instance.pk}/",
        )