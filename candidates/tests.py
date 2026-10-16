from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Candidate

User = get_user_model()

class CandidateModelTestCase(TestCase):
    def setUp(self):
        # Creamos un usuario de prueba
        self.user = User.objects.create_user(username='candidato_test', password='password123')

    def test_candidate_creation(self):
        # 1. Test de creación con sus campos correspondientes
        candidate = Candidate.objects.create(
            user=self.user,
            availability="Inmediata",
            interests="Python, Django, Backend",
            allows_contact=True
        )
        self.assertEqual(candidate.user.username, "candidato_test")
        self.assertEqual(candidate.availability, "Inmediata")
        self.assertTrue(candidate.allows_contact)

    def test_user_candidate_profile_relationship(self):
        # 2. Test del acceso inverso: user.candidate_profile
        candidate = Candidate.objects.create(
            user=self.user,
            availability="Part-time",
            interests="React",
            allows_contact=False
        )
        # Comprobamos que desde el objeto 'user' podemos llegar al 'candidate' gracias al related_name
        self.assertEqual(self.user.candidate_profile, candidate)
