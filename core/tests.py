
from django.test import TestCase
from django.db import IntegrityError, transaction

from organizations.models import Organization, OrganizationKind
from .models import Skill


class OrganizationModelTests(TestCase):
    def test_str_returns_name(self):
        org = Organization.objects.create(name="Acme", slug="acme")
        self.assertEqual(str(org), "Acme")

    def test_default_kind_is_company(self):
        org = Organization.objects.create(name="Acme", slug="acme")
        self.assertEqual(org.kind, OrganizationKind.COMPANY)

    def test_name_must_be_unique(self):
        Organization.objects.create(name="Acme", slug="acme")
        with self.assertRaises(IntegrityError):
            Organization.objects.create(name="Acme", slug="acme-2")

    def test_slug_must_be_unique(self):
        Organization.objects.create(name="Acme", slug="acme")
        with self.assertRaises(IntegrityError):
            Organization.objects.create(name="Otra", slug="acme")


class SkillModelTests(TestCase):
    def test_str_returns_name(self):
        skill = Skill.objects.create(name="Python")
        self.assertEqual(str(skill), "Python")

    def test_slug_is_generated_automatically(self):
        skill = Skill.objects.create(name="Machine Learning")
        self.assertEqual(skill.slug, "machine-learning")

    def test_name_must_be_unique(self):
        Skill.objects.create(name="Python")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Skill.objects.create(name="Python")
