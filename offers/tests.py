from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Offer, StatusChoices
from organizations.models import Organization
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class OfferModelTestCase(TestCase):
    def setUp(self):
        # Configuración inicial de datos simulados para las pruebas
        self.user = User.objects.create_user(username='tester', password='password123')
        self.org = Organization.objects.create(name="Empresa de Prueba")

    def test_offer_creation_and_default_status(self):
        # Prueba que la oferta se almacena correctamente y toma el estado por defecto
        offer = Offer.objects.create(
            organization=self.org,
            created_by=self.user,
            title="Python Developer",
            slug="python-developer",
            description="Oferta de prueba",
            location="Remoto"
        )
        self.assertEqual(offer.title, "Python Developer")
        self.assertEqual(offer.status, StatusChoices.BORRADOR)

    def test_organization_offers_relationship(self):
        # Prueba la relación inversa mediante el related_name='offers'
        offer = Offer.objects.create(
            organization=self.org,
            created_by=self.user,
            title="Frontend Developer",
            slug="frontend-developer",
            description="Detalles de la oferta",
            location="Híbrido"
        )
        # Verifica que la oferta figure en la lista interna de la organización
        self.assertIn(offer, self.org.offers.all())



class OfferPermissionTests(APITestCase):
    def setUp(self):
        self.candidate = User.objects.create_user(
            username="candidate_test",
            email="candidate_test@example.com",
            password="test-password-123",
            role=User.Role.CANDIDATE,
        )
        self.recruiter = User.objects.create_user(
            username="recruiter_test",
            email="recruiter_test@example.com",
            password="test-password-123",
            role=User.Role.RECRUITER,
        )
        self.org = Organization.objects.create(
            name="Empresa API Test",
            slug="empresa-api-test",
        )
        self.offer = Offer.objects.create(
            organization=self.org,
            created_by=self.recruiter,
            title="Oferta para pruebas API",
            slug="oferta-pruebas-api",
            description="Oferta creada para probar permisos.",
            location="Remoto",
            status=StatusChoices.PUBLICADA,
        )
        self.url = reverse("offer-detail", args=[self.offer.pk])

    def test_candidate_cannot_delete_offer(self):
        self.client.force_authenticate(user=self.candidate)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())

    def test_recruiter_can_delete_offer(self):
        self.client.force_authenticate(user=self.recruiter)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=self.offer.pk).exists())
