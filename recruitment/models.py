
from django.conf import settings
from django.db import models


class Task(models.Model):

    class TaskType(models.TextChoices):
        CALL = "CALL", "Próxima llamada"
        FEEDBACK = "FEEDBACK", "Feedback pendiente"
        INTERVIEW = "INTERVIEW", "Entrevista"
        TEST = "TEST", "Prueba"
        FOLLOW_UP = "FOLLOW_UP", "Seguimiento"
        OTHER = "OTHER", "Otro"

    class Priority(models.TextChoices):
        LOW = "LOW", "Baja"
        MEDIUM = "MEDIUM", "Media"
        HIGH = "HIGH", "Alta"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        IN_PROGRESS = "IN_PROGRESS", "En progreso"
        COMPLETED = "COMPLETED", "Completada"

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.OTHER,
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    due_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title
