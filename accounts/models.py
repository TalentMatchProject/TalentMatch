from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator



class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidato"
        HEADHUNTER = "headhunter", "Headhunter"
        RECRUITER = "recruiter", "Recruiter de empresa"

    email = models.EmailField("correo electrónico", unique=True)
    role = models.CharField(
        "rol",
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE,
    )
    phone = models.CharField(
        "teléfono",
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                r"^\+?[0-9 ]{9,20}$",
                "Introduce un teléfono válido, por ejemplo +34 600 000 000.",
            )
        ],
    )
    city = models.CharField("ciudad", max_length=100, blank=True)
    professional_title = models.CharField("perfil profesional", max_length=100,blank=True)
    bio = models.TextField("biografía", blank=True)
    avatar = models.ImageField("avatar", upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.username

    
