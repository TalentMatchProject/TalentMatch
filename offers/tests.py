from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import ProtectedError
from .models import Offer, OfferSkill, StatusChoices
from organizations.models import Organization, Skill  # Importamos los modelos de tus compañeros

User = get_user_model()

# =====================================================================
# 1. TESTS DE LA PRIMERA TAREA (OFFER) - Los tuyos actuales
# =====================================================================
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


# =====================================================================
# 2. TESTS DE LA NUEVA TAREA (OFFERSKILL)
# =====================================================================
class OfferSkillTestCase(TestCase):
    def setUp(self):
        # Datos necesarios para probar las competencias de la oferta
        self.user = User.objects.create_user(username='skill_tester', password='password123')
        self.org = Organization.objects.create(name="Empresa Skill Test", slug="empresa-skill-test")
        self.offer = Offer.objects.create(
            organization=self.org,
            created_by=self.user,
            title="Django Developer",
            slug="django-developer",
            description="Buscar programador experto",
            location="Remoto"
        )
        # Creamos la competencia base de la app de tus compañeros
        self.skill = Skill.objects.create(name="Django", slug="django", is_active=True)

    def test_offer_skill_creation_and_relationship(self):
        # 1. Test de creación y relación inversa offer.offer_skills
        offer_skill = OfferSkill.objects.create(
            offer=self.offer,
            skill=self.skill,
            requirement=OfferSkill.RequirementChoices.IMPRESCINDIBLE
        )
        self.assertEqual(offer_skill.skill.name, "Django")
        # Verifica que podemos acceder a la lista desde 'offer.offer_skills'
        self.assertIn(offer_skill, self.offer.offer_skills.all())

    def test_offer_skill_uniqueness(self):
        # 2. Test de unicidad: Una oferta no repite la misma skill
        OfferSkill.objects.create(
            offer=self.offer,
            skill=self.skill,
            requirement=OfferSkill.RequirementChoices.IMPRESCINDIBLE
        )
        # Intentar crear otra fila con la misma oferta y misma skill debe dar IntegrityError
        with self.assertRaises(IntegrityError):
            OfferSkill.objects.create(
                offer=self.offer,
                skill=self.skill,
                requirement=OfferSkill.RequirementChoices.DESEABLE
            )

    def test_offer_skill_protected_error(self):
        # 3. Test de ProtectedError: skill (PROTECT)
        OfferSkill.objects.create(
            offer=self.offer,
            skill=self.skill,
            requirement=OfferSkill.RequirementChoices.DESEABLE
        )
        # Intentar borrar la Skill general de la base de datos debe fallar con ProtectedError
        with self.assertRaises(ProtectedError):
            self.skill.delete()

