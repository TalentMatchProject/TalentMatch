from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Offer, StatusChoices
from organizations.models import Organization 

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
