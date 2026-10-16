from django.db import models
from django.conf import settings

class Candidate(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate_profile')
    availability = models.TextField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    allows_contact = models.BooleanField(default=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class CandidateSkill(models.Model):
    class SourceChoices(models.TextChoices):
        CV = 'CV', 'CV'
        PROYECTO = 'proyecto', 'Proyecto'
        CERTIFICACION = 'certificacion', 'Certificación'
        ENTREVISTA = 'entrevista', 'Entrevista'

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='candidate_skills')
    # Ponemos la relación como texto. Django la buscará automáticamente cuando se fusione la otra tarea
    skill = models.ForeignKey('organizations.Skill', on_delete=models.PROTECT, related_name='candidate_skills')
    
    evidence = models.TextField()
    source = models.CharField(max_length=20, choices=SourceChoices.choices, default=SourceChoices.CV)

    class Meta:
        unique_together = ('candidate', 'skill')

    def __str__(self):
        return f"Competencia de {self.candidate.user.username}"

