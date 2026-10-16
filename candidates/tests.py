from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import ProtectedError
from core.models import Skill
from .models import Candidate, CandidateSkill, CandidateSkillSource

User = get_user_model()

# ==========================================
# 1. TESTS DE LA TAREA ANTERIOR (CANDIDATE)
# ==========================================
class CandidateModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='candidato_test', password='password123')

    def test_candidate_creation(self):
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
        candidate = Candidate.objects.create(
            user=self.user,
            availability="Part-time",
            interests="React",
            allows_contact=False
        )
        self.assertEqual(self.user.candidate_profile, candidate)


# ==========================================
# 2. TESTS DE LA TAREA DE HOY (CANDIDATESKILL)
# ==========================================
class CandidateSkillTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='candidate_user', password='password123')
        self.candidate = Candidate.objects.create(user=self.user, availability="Inmediata")
        self.skill = Skill.objects.create(name="Python", slug="python", is_active=True)

    def test_candidate_skill_creation(self):
        candidate_skill = CandidateSkill.objects.create(
            candidate=self.candidate,
            skill=self.skill,
            evidence="Desarrollo del Backend de la plataforma",
            source=CandidateSkillSource.PROJECT
        )
        self.assertEqual(candidate_skill.skill.name, "Python")
        self.assertEqual(candidate_skill.source, "project")

    def test_candidate_skill_uniqueness(self):
        CandidateSkill.objects.create(
            candidate=self.candidate,
            skill=self.skill,
            evidence="Primera evidencia",
            source=CandidateSkillSource.CV
        )
        with self.assertRaises(IntegrityError):
            CandidateSkill.objects.create(
                candidate=self.candidate,
                skill=self.skill,
                evidence="Segunda evidencia del mismo skill",
                source=CandidateSkillSource.INTERVIEW
            )

    def test_candidate_skill_protected_error(self):
        CandidateSkill.objects.create(
            candidate=self.candidate,
            skill=self.skill,
            evidence="Evidencia para proteger",
            source=CandidateSkillSource.CERTIFICATION
        )
        with self.assertRaises(ProtectedError):
            self.skill.delete()
