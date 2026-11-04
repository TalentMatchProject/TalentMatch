from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chat.services import get_or_create_conversation, send_message
from offers.models import Offer, SavedOffer, StatusChoices
from organizations.models import Membership, MembershipRole, Organization

from .models import Notification, NotificationType
from .tasks import create_notification_async

User = get_user_model()
PASSWORD = "Password123!"


def create_data(test):
    test.org = Organization.objects.create(name="Tech Global", slug="tech-global")
    test.recruiter = User.objects.create_user(
        username="rita", email="rita@example.com", password=PASSWORD, role="recruiter"
    )
    test.colleague = User.objects.create_user(
        username="hugo", email="hugo@example.com", password=PASSWORD, role="headhunter"
    )
    test.candidate = User.objects.create_user(
        username="carla", email="carla@example.com", password=PASSWORD, role="candidate"
    )
    Membership.objects.create(user=test.recruiter, organization=test.org, role=MembershipRole.RECRUITER)
    Membership.objects.create(user=test.colleague, organization=test.org, role=MembershipRole.HEADHUNTER)
    test.offer = Offer.objects.create(
        organization=test.org,
        created_by=test.recruiter,
        title="Backend Django",
        description="Oferta backend",
        location="Barcelona",
        status=StatusChoices.PUBLICADA,
    )


class ChatNotificationTests(TestCase):
    def setUp(self):
        create_data(self)
        self.conversation, _ = get_or_create_conversation(self.candidate, self.offer.pk)

    def test_candidate_message_notifies_every_member(self):
        send_message(self.candidate, self.conversation.pk, "Hola, ¿sigue abierta?")
        self.assertEqual(Notification.objects.filter(recipient=self.recruiter).count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.colleague).count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.candidate).count(), 0)
        notification = Notification.objects.get(recipient=self.recruiter)
        self.assertEqual(notification.notification_type, NotificationType.NEW_MESSAGE)
        self.assertFalse(notification.is_read)
        self.assertIn("carla", notification.body)
        self.assertEqual(
            notification.link,
            f"/api/v1/conversations/{self.conversation.pk}/messages/",
        )

    def test_member_message_notifies_only_the_candidate(self):
        send_message(self.recruiter, self.conversation.pk, "Sí, te llamamos mañana.")
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.get().recipient, self.candidate)

    def test_long_messages_are_shortened_in_the_notification(self):
        send_message(self.recruiter, self.conversation.pk, "a" * 200)
        body = Notification.objects.get().body
        self.assertTrue(body.endswith("..."))
        self.assertLess(len(body), 100)

    def test_chat_keeps_working_if_the_queue_fails(self):
        with self.assertLogs("notifications.signals", level="ERROR"):
            with patch(
                "notifications.signals.create_notification_async.delay",
                side_effect=Exception("Redis caído"),
            ):
                message = send_message(self.candidate, self.conversation.pk, "Hola")
        self.assertIsNotNone(message.pk)
        self.assertEqual(Notification.objects.count(), 0)


class OfferNotificationTests(TestCase):
    def setUp(self):
        create_data(self)

    def test_saving_an_offer_notifies_the_members(self):
        SavedOffer.objects.create(user=self.candidate, offer=self.offer)
        recipients = set(Notification.objects.values_list("recipient", flat=True))
        self.assertEqual(recipients, {self.recruiter.pk, self.colleague.pk})
        notification = Notification.objects.filter(recipient=self.recruiter).get()
        self.assertEqual(notification.notification_type, NotificationType.OFFER_SAVED)

    def test_closing_an_offer_notifies_those_who_saved_it(self):
        SavedOffer.objects.create(user=self.candidate, offer=self.offer)
        Notification.objects.all().delete()

        self.offer.status = StatusChoices.CERRADA
        self.offer.save()

        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.candidate)
        self.assertEqual(notification.notification_type, NotificationType.OFFER_UNAVAILABLE)

    def test_other_changes_do_not_notify(self):
        SavedOffer.objects.create(user=self.candidate, offer=self.offer)
        Notification.objects.all().delete()

        self.offer.title = "Backend Django Senior"
        self.offer.save()
        self.assertEqual(Notification.objects.count(), 0)

    def test_creating_an_offer_does_not_notify(self):
        Notification.objects.all().delete()
        Offer.objects.create(
            organization=self.org,
            title="Otra",
            description="d",
            location="l",
            status=StatusChoices.PUBLICADA,
        )
        self.assertEqual(Notification.objects.count(), 0)


class NotificationTaskTests(TestCase):
    def setUp(self):
        create_data(self)

    def test_task_creates_notification_and_sends_email(self):
        with self.assertLogs("notifications.tasks", level="INFO") as logs:
            result = create_notification_async.delay(
                self.candidate.pk,
                NotificationType.SYSTEM,
                "Bienvenida",
                "Gracias por registrarte",
            )
        self.assertIn("registrada", result.get())
        self.assertEqual(Notification.objects.get().title, "Bienvenida")
        self.assertTrue(any("carla@example.com" in line for line in logs.output))

    def test_task_with_unknown_recipient_does_nothing(self):
        result = create_notification_async.delay(9999, NotificationType.SYSTEM, "x", "y")
        self.assertEqual(result.get(), "Destinatario no encontrado.")
        self.assertEqual(Notification.objects.count(), 0)


class NotificationAPITests(APITestCase):
    def setUp(self):
        create_data(self)
        self.mine = Notification.objects.create(
            recipient=self.candidate, title="Mía", body="b", notification_type=NotificationType.SYSTEM
        )
        self.read = Notification.objects.create(
            recipient=self.candidate, title="Leída", body="b", is_read=True
        )
        self.other = Notification.objects.create(recipient=self.recruiter, title="Ajena", body="b")
        self.list_url = reverse("notification-list")

    def test_anonymous_cannot_list(self):
        self.assertIn(
            self.client.get(self.list_url).status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_user_only_sees_own_notifications(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.get(self.list_url)
        titles = {item["title"] for item in response.data["results"]}
        self.assertEqual(titles, {"Mía", "Leída"})

    def test_filter_unread(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.get(self.list_url, {"is_read": "false"})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Mía")

    def test_mark_one_as_read(self):
        self.client.force_authenticate(user=self.candidate)
        url = reverse("notification-read", kwargs={"pk": self.mine.pk})
        self.assertEqual(self.client.post(url).status_code, status.HTTP_200_OK)
        self.mine.refresh_from_db()
        self.assertTrue(self.mine.is_read)

    def test_cannot_mark_someone_elses_notification(self):
        self.client.force_authenticate(user=self.candidate)
        url = reverse("notification-read", kwargs={"pk": self.other.pk})
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)
        self.other.refresh_from_db()
        self.assertFalse(self.other.is_read)

    def test_mark_all_as_read_only_affects_the_user(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.post(reverse("notification-mark-all-read"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Notification.objects.filter(recipient=self.candidate, is_read=False).exists())
        self.other.refresh_from_db()
        self.assertFalse(self.other.is_read)

    def test_schema_still_builds(self):
        self.assertEqual(self.client.get(reverse("schema")).status_code, status.HTTP_200_OK)
