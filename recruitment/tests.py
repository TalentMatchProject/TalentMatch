from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from recruitment.models import Task


class TaskModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_task_is_created(self):
        task = Task.objects.create(
            owner=self.user,
            title="Llamar candidato",
            due_date=timezone.now()
        )

        self.assertEqual(task.owner, self.user)

    def test_default_status_is_pending(self):
        task = Task.objects.create(
            owner=self.user,
            title="Llamar candidato",
            due_date=timezone.now()
        )

        self.assertEqual(
            task.status,
            Task.Status.PENDING
        )

    def test_user_tasks_relationship(self):
        task = Task.objects.create(
            owner=self.user,
            title="Llamar candidato",
            due_date=timezone.now()
        )

        self.assertIn(
            task,
            self.user.tasks.all()
        )