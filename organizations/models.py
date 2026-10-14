from django.db import models


class OrganizationKind(models.TextChoices):
    COMPANY = "company", "Empresa"
    HEADHUNTING_FIRM = "headhunting_firm", "Firma de headhunting"


class Organization(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True)
    kind = models.CharField(
        max_length=20,
        choices=OrganizationKind.choices,
        default=OrganizationKind.COMPANY,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
