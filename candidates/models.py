from django.db import models


class CandidateSkillSource(models.TextChoices):
    CV = "cv", "CV"
    PROJECT = "project", "Proyecto"
    CERTIFICATION = "certification", "Certificación"
    INTERVIEW = "interview", "Entrevista"
