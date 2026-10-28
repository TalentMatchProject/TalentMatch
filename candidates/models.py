from django.db import models
from django.conf import settings


class Candidate(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate_profile')
    availability = models.TextField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    allows_contact = models.BooleanField(default=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
      
class CandidateSkillSource(models.TextChoices):
    CV = "cv", "CV"
    PROJECT = "project", "Proyecto"
    CERTIFICATION = "certification", "Certificación"
    INTERVIEW = "interview", "Entrevista"


class CandidateSkill(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='candidate_skills')
    skill = models.ForeignKey('core.Skill', on_delete=models.PROTECT, related_name='candidate_skills')

    evidence = models.TextField()
    source = models.CharField(max_length=20, choices=CandidateSkillSource.choices, default=CandidateSkillSource.CV)

    class Meta:
        unique_together = ('candidate', 'skill')

    def __str__(self):
        return f"Competencia de {self.candidate.user.username}"
