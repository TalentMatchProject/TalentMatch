from django.db import models
from django.conf import settings


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


class MembershipRole(models.TextChoices):
    ADMIN = "admin", "Administrador"
    HEADHUNTER = "headhunter", "Headhunter"
    RECRUITER = "recruiter", "Recruiter"


class Membership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.RECRUITER,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization",
            ),
        ]

    def __str__(self):
        return f"{self.user} en {self.organization} ({self.get_role_display()})"



class Skill(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
