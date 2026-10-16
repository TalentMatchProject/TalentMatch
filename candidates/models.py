from django.db import models
from django.conf import settings


class Candidate(models.Model):
    # Relación uno a uno con el usuario. Si se borra el usuario, se borra su perfil de candidato (CASCADE)
    # related_name='candidate_profile' cumple con el requisito del test inverso
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='candidate_profile'
    )
    
    # Campos de texto libres para disponibilidad e intereses
    availability = models.TextField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    
    # Campo booleano para permitir contacto (por defecto Verdadero o Falso según prefiráis)
    allows_contact = models.BooleanField(default=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class CandidateSkillSource(models.TextChoices):
    CV = "cv", "CV"
    PROJECT = "project", "Proyecto"
    CERTIFICATION = "certification", "Certificación"
    INTERVIEW = "interview", "Entrevista"
