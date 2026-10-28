from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Skill
from offers.models import Offer, OfferSkill, SavedOffer, StatusChoices
from organizations.models import Membership, MembershipRole, Organization

User = get_user_model()
PASSWORD = "TestPassword123!"


class OfferAPITests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Tech Global", slug="tech-global")
        self.other_org = Organization.objects.create(name="Alpha", slug="alpha")

        self.member = User.objects.create_user(
            username="rita", email="rita@example.com", password=PASSWORD, role="recruiter"
        )
        self.other_member = User.objects.create_user(
            username="hugo", email="hugo@example.com", password=PASSWORD, role="recruiter"
        )
        self.candidate = User.objects.create_user(
            username="carla", email="carla@example.com", password=PASSWORD, role="candidate"
        )
        Membership.objects.create(user=self.member, organization=self.org, role=MembershipRole.RECRUITER)
        Membership.objects.create(user=self.other_member, organization=self.other_org, role=MembershipRole.RECRUITER)

        self.python = Skill.objects.create(name="Python")
        self.offer = Offer.objects.create(
            organization=self.org,
            created_by=self.member,
            title="Backend Django",
            description="Oferta backend",
            location="Barcelona",
            modality="remoto",
            status=StatusChoices.PUBLICADA,
            salary_min=Decimal("40000"),
            salary_max=Decimal("55000"),
        )
        OfferSkill.objects.create(offer=self.offer, skill=self.python)
        self.draft = Offer.objects.create(
            organization=self.org,
            created_by=self.member,
            title="Borrador interno",
            description="Aun no publicada",
            location="Madrid",
        )
        self.detail = reverse("offer-detail", kwargs={"pk": self.offer.pk})
        self.payload = {
            "organization": self.org.pk,
            "title": "Frontend React",
            "description": "Oferta frontend",
            "location": "Remoto",
            "modality": "remoto",
            "salary_min": "30000",
            "salary_max": "45000",
        }

    def test_offer_list_is_public(self):
        response = self.client.get(reverse("offer-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in response.data["results"]]
        self.assertIn("Backend Django", titles)

    def test_drafts_are_hidden_from_visitors(self):
        response = self.client.get(reverse("offer-list"))
        titles = [item["title"] for item in response.data["results"]]
        self.assertNotIn("Borrador interno", titles)

    def test_members_can_see_their_drafts(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get(reverse("offer-list"))
        titles = [item["title"] for item in response.data["results"]]
        self.assertIn("Borrador interno", titles)

    def test_drafts_are_hidden_from_other_organizations(self):
        self.client.force_authenticate(user=self.other_member)
        response = self.client.get(reverse("offer-list"))
        titles = [item["title"] for item in response.data["results"]]
        self.assertNotIn("Borrador interno", titles)

    def test_offer_detail_returns_200(self):
        response = self.client.get(self.detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["offer_skills"][0]["skill_detail"]["name"], "Python")

    def test_anonymous_cannot_create_offer(self):
        response = self.client.post(reverse("offer-list"), self.payload, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_non_member_cannot_create_offer(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.post(reverse("offer-list"), self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_create_offer_with_server_side_author(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse("offer-list"), self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offer = Offer.objects.get(title="Frontend React")
        self.assertEqual(offer.created_by, self.member)
        self.assertEqual(offer.slug, "frontend-react")
        self.assertEqual(offer.status, StatusChoices.BORRADOR)

    def test_two_offers_with_same_title_get_different_slugs(self):
        self.client.force_authenticate(user=self.member)
        first = self.client.post(reverse("offer-list"), self.payload, format="json")
        second = self.client.post(reverse("offer-list"), self.payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(first.data["slug"], second.data["slug"])

    def test_cannot_create_offer_in_another_organization(self):
        self.client.force_authenticate(user=self.member)
        payload = dict(self.payload, organization=self.other_org.pk)
        response = self.client.post(reverse("offer-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_salary_max_cannot_be_lower_than_min(self):
        self.client.force_authenticate(user=self.member)
        payload = dict(self.payload, salary_min="5000", salary_max="1000")
        response = self.client.post(reverse("offer-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_can_update_offer(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(self.detail, {"title": "Backend Senior"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Backend Senior")

    def test_other_organization_cannot_update_offer(self):
        self.client.force_authenticate(user=self.other_member)
        response = self.client.patch(self.detail, {"title": "Hack"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_candidate_cannot_update_offer(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.patch(self.detail, {"title": "Hack"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_delete_offer(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.delete(self.detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_organization_cannot_delete_offer(self):
        self.client.force_authenticate(user=self.other_member)
        response = self.client.delete(self.detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())

    def test_filter_by_modality(self):
        response = self.client.get(reverse("offer-list"), {"modality": "remoto"})
        self.assertEqual(response.data["count"], 1)
        response = self.client.get(reverse("offer-list"), {"modality": "presencial"})
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_min_salary(self):
        response = self.client.get(reverse("offer-list"), {"min_salary": "45000"})
        self.assertEqual(response.data["count"], 0)
        response = self.client.get(reverse("offer-list"), {"min_salary": "40000"})
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_skill(self):
        response = self.client.get(reverse("offer-list"), {"skill": self.python.pk})
        self.assertEqual(response.data["count"], 1)

    def test_search_offers(self):
        response = self.client.get(reverse("offer-list"), {"search": "Django"})
        self.assertEqual(response.data["count"], 1)
        response = self.client.get(reverse("offer-list"), {"search": "zzzz"})
        self.assertEqual(response.data["count"], 0)

    def test_ordering_by_salary(self):
        Offer.objects.create(
            organization=self.org,
            title="Oferta barata",
            description="d",
            location="l",
            status=StatusChoices.PUBLICADA,
            salary_min=Decimal("20000"),
        )
        response = self.client.get(reverse("offer-list"), {"ordering": "salary_min"})
        self.assertEqual(response.data["results"][0]["title"], "Oferta barata")

    def test_organizations_are_read_only(self):
        self.assertEqual(self.client.get(reverse("organization-list")).status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse("organization-list"), {"name": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_skills_are_read_only(self):
        self.assertEqual(self.client.get(reverse("skill-list")).status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse("skill-list"), {"name": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_candidate_can_save_and_unsave_offer(self):
        self.client.force_authenticate(user=self.candidate)
        url = reverse("offer-save", kwargs={"pk": self.offer.pk})
        first = self.client.post(url)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SavedOffer.objects.filter(user=self.candidate, offer=self.offer).exists())
        second = self.client.post(url)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertFalse(SavedOffer.objects.filter(user=self.candidate, offer=self.offer).exists())

    def test_member_cannot_save_own_organization_offer(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(reverse("offer-save", kwargs={"pk": self.offer.pk}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_saved_offers_are_private(self):
        SavedOffer.objects.create(user=self.candidate, offer=self.offer)
        self.assertIn(
            self.client.get(reverse("saved-offer-list")).status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
        self.client.force_authenticate(user=self.other_member)
        self.assertEqual(self.client.get(reverse("saved-offer-list")).data["count"], 0)
        self.client.force_authenticate(user=self.candidate)
        self.assertEqual(self.client.get(reverse("saved-offer-list")).data["count"], 1)

    def test_popular_offers_are_ordered_by_saves(self):
        popular = Offer.objects.create(
            organization=self.org, title="Muy guardada", description="d",
            location="l", status=StatusChoices.PUBLICADA,
        )
        SavedOffer.objects.create(user=self.candidate, offer=popular)
        response = self.client.get(reverse("popular-offers"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Muy guardada")

    def test_openapi_schema_and_docs(self):
        self.assertEqual(self.client.get(reverse("schema")).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse("swagger-ui")).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse("redoc")).status_code, status.HTTP_200_OK)