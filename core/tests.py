from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Skill


class SkillModelTests(TestCase):
    def test_str_returns_name(self):
        skill = Skill.objects.create(name="Python")
        self.assertEqual(str(skill), "Python")

    def test_slug_is_generated_automatically(self):
        skill = Skill.objects.create(name="Machine Learning")
        self.assertEqual(skill.slug, "machine-learning")

    def test_is_active_defaults_to_true(self):
        skill = Skill.objects.create(name="Django")
        self.assertTrue(skill.is_active)

    def test_name_must_be_unique(self):
        Skill.objects.create(name="Python")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Skill.objects.create(name="Python")

    def test_slug_must_be_unique(self):
        Skill.objects.create(name="Python", slug="python")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Skill.objects.create(name="Python avanzado", slug="python")