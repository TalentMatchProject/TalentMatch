from django.test import TestCase
from django.db import IntegrityError

from .models import Organization, OrganizationKind


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
