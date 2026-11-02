from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from candidates.models import Candidate
from offers.models import Offer, StatusChoices
from organizations.models import Membership, MembershipRole, Organization

from .models import Conversation, Message
from .services import (
    get_or_create_conversation,
    mark_messages_as_read,
    send_message,
)

User = get_user_model()
PASSWORD = "Password123!"


def create_data(test):
    test.org = Organization.objects.create(name="Tech Global", slug="tech-global")
    test.recruiter = User.objects.create_user(
        username="rita", email="rita@example.com", password=PASSWORD, role="recruiter"
    )
    test.colleague = User.objects.create_user(
        username="hugo", email="hugo@example.com", password=PASSWORD, role="recruiter"
    )
    test.candidate = User.objects.create_user(
        username="carla", email="carla@example.com", password=PASSWORD, role="candidate"
    )
    test.intruder = User.objects.create_user(
        username="ivan", email="ivan@example.com", password=PASSWORD, role="candidate"
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
    test.draft = Offer.objects.create(
        organization=test.org,
        title="Borrador",
        description="Sin publicar",
        location="Madrid",
    )


class ChatServiceTests(TestCase):
    def setUp(self):
        create_data(self)

    def test_candidate_can_start_conversation(self):
        conversation, created = get_or_create_conversation(self.candidate, self.offer.pk)
        self.assertTrue(created)
        self.assertEqual(conversation.candidate, self.candidate)
        self.assertEqual(conversation.offer, self.offer)

    def test_same_conversation_is_reused(self):
        first, _ = get_or_create_conversation(self.candidate, self.offer.pk)
        second, created = get_or_create_conversation(self.candidate, self.offer.pk)
        self.assertFalse(created)
        self.assertEqual(first.pk, second.pk)

    def test_member_cannot_start_chat_on_own_organization_offer(self):
        with self.assertRaises(ValidationError):
            get_or_create_conversation(self.recruiter, self.offer.pk)

    def test_cannot_start_chat_on_unpublished_offer(self):
        with self.assertRaises(ValidationError):
            get_or_create_conversation(self.candidate, self.draft.pk)

    def test_member_can_contact_candidate_who_allows_contact(self):
        Candidate.objects.create(user=self.candidate, allows_contact=True)
        conversation, created = get_or_create_conversation(
            self.recruiter, self.offer.pk, candidate_id=self.candidate.pk
        )
        self.assertTrue(created)
        self.assertEqual(conversation.candidate, self.candidate)

    def test_member_cannot_contact_candidate_who_blocks_contact(self):
        Candidate.objects.create(user=self.candidate, allows_contact=False)
        with self.assertRaises(ValidationError):
            get_or_create_conversation(
                self.recruiter, self.offer.pk, candidate_id=self.candidate.pk
            )

    def test_member_cannot_contact_candidate_without_profile(self):
        with self.assertRaises(ValidationError):
            get_or_create_conversation(
                self.recruiter, self.offer.pk, candidate_id=self.candidate.pk
            )

    def test_non_member_cannot_contact_candidates(self):
        Candidate.objects.create(user=self.candidate, allows_contact=True)
        with self.assertRaises(PermissionDenied):
            get_or_create_conversation(
                self.intruder, self.offer.pk, candidate_id=self.candidate.pk
            )

    def test_candidate_and_members_can_send_messages(self):
        conversation, _ = get_or_create_conversation(self.candidate, self.offer.pk)
        first = send_message(self.candidate, conversation.pk, "¿Hay teletrabajo?")
        second = send_message(self.recruiter, conversation.pk, "Sí, es remoto.")
        third = send_message(self.colleague, conversation.pk, "Te llamamos mañana.")
        self.assertEqual(first.sender, self.candidate)
        self.assertEqual(second.sender, self.recruiter)
        self.assertEqual(third.sender, self.colleague)
        self.assertFalse(first.is_read)

    def test_intruder_cannot_send_message(self):
        conversation, _ = get_or_create_conversation(self.candidate, self.offer.pk)
        with self.assertRaises(PermissionDenied):
            send_message(self.intruder, conversation.pk, "Intento colarme")

    def test_empty_message_is_rejected(self):
        conversation, _ = get_or_create_conversation(self.candidate, self.offer.pk)
        with self.assertRaises(ValidationError):
            send_message(self.candidate, conversation.pk, "   ")

    def test_messages_are_marked_as_read_by_the_other_side(self):
        conversation, _ = get_or_create_conversation(self.candidate, self.offer.pk)
        from_candidate = send_message(self.candidate, conversation.pk, "Hola")
        from_member = send_message(self.recruiter, conversation.pk, "Buenas")

        mark_messages_as_read(conversation.pk, self.colleague)
        from_candidate.refresh_from_db()
        from_member.refresh_from_db()
        self.assertTrue(from_candidate.is_read)
        self.assertFalse(from_member.is_read)

        mark_messages_as_read(conversation.pk, self.candidate)
        from_member.refresh_from_db()
        self.assertTrue(from_member.is_read)

    def test_intruder_cannot_mark_messages_as_read(self):
        conversation, _ = get_or_create_conversation(self.candidate, self.offer.pk)
        with self.assertRaises(PermissionDenied):
            mark_messages_as_read(conversation.pk, self.intruder)


class ChatAPITests(APITestCase):
    def setUp(self):
        create_data(self)
        self.list_url = reverse("conversation-list")

    def start(self, user=None, **extra):
        self.client.force_authenticate(user=user or self.candidate)
        return self.client.post(
            self.list_url, {"offer": self.offer.pk, **extra}, format="json"
        )

    def test_anonymous_cannot_use_chat(self):
        response = self.client.get(self.list_url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_candidate_starts_conversation_and_reuses_it(self):
        first = self.start()
        second = self.start()
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(Conversation.objects.count(), 1)

    def test_member_cannot_start_conversation_as_candidate(self):
        response = self.start(user=self.recruiter)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_on_unknown_offer_returns_404(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.post(self.list_url, {"offer": 9999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_member_cannot_contact_a_candidate(self):
        Candidate.objects.create(user=self.candidate, allows_contact=True)
        response = self.start(user=self.intruder, candidate=self.candidate.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_each_user_only_sees_their_conversations(self):
        self.start()
        self.client.force_authenticate(user=self.candidate)
        self.assertEqual(self.client.get(self.list_url).data["count"], 1)
        self.client.force_authenticate(user=self.colleague)
        self.assertEqual(self.client.get(self.list_url).data["count"], 1)
        self.client.force_authenticate(user=self.intruder)
        self.assertEqual(self.client.get(self.list_url).data["count"], 0)

    def test_intruder_cannot_open_a_conversation(self):
        conversation_id = self.start().data["id"]
        self.client.force_authenticate(user=self.intruder)
        detail = reverse("conversation-detail", kwargs={"pk": conversation_id})
        send = reverse("conversation-send", kwargs={"pk": conversation_id})
        messages = reverse("conversation-messages", kwargs={"pk": conversation_id})
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.post(send, {"text": "hola"}).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get(messages).status_code, status.HTTP_404_NOT_FOUND)

    def test_send_and_read_messages(self):
        conversation_id = self.start().data["id"]
        send = reverse("conversation-send", kwargs={"pk": conversation_id})
        messages = reverse("conversation-messages", kwargs={"pk": conversation_id})

        self.client.force_authenticate(user=self.candidate)
        response = self.client.post(send, {"text": "Hola, ¿sigue abierta?"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["sender_username"], "carla")

        self.client.force_authenticate(user=self.recruiter)
        detail = reverse("conversation-detail", kwargs={"pk": conversation_id})
        self.assertEqual(self.client.get(detail).data["unread_count"], 1)
        response = self.client.get(messages)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.client.get(detail).data["unread_count"], 0)
        self.assertTrue(Message.objects.get().is_read)

    def test_empty_message_returns_400(self):
        conversation_id = self.start().data["id"]
        send = reverse("conversation-send", kwargs={"pk": conversation_id})
        response = self.client.post(send, {"text": "   "}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_too_long_message_returns_400(self):
        conversation_id = self.start().data["id"]
        send = reverse("conversation-send", kwargs={"pk": conversation_id})
        response = self.client.post(send, {"text": "a" * 1001}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conversation_shows_last_message(self):
        conversation_id = self.start().data["id"]
        send = reverse("conversation-send", kwargs={"pk": conversation_id})
        self.client.post(send, {"text": "Primero"}, format="json")
        self.client.post(send, {"text": "Último"}, format="json")
        detail = reverse("conversation-detail", kwargs={"pk": conversation_id})
        self.assertEqual(self.client.get(detail).data["last_message"], "Último")

    def test_schema_still_builds(self):
        self.assertEqual(self.client.get(reverse("schema")).status_code, status.HTTP_200_OK)
