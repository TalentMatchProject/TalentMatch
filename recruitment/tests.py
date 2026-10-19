from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
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

class TaskOwnershipTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user1 = User.objects.create_user(
            username="candidata1",
            email="candidata1@test.com",
            password="TestPassword123!",
        )

        self.user2 = User.objects.create_user(
            username="candidata2",
            email="candidata2@test.com",
            password="TestPassword123!",
        )

        self.task1 = Task.objects.create(
            title="Llamar a una empresa",
            owner=self.user1,
            task_type=Task.TaskType.CALL,
            priority=Task.Priority.MEDIUM,
            status=Task.Status.PENDING,
            due_date=timezone.now() + timedelta(days=1),
        )

        self.task2 = Task.objects.create(
            title="Preparar una entrevista",
            owner=self.user2,
            task_type=Task.TaskType.INTERVIEW,
            priority=Task.Priority.HIGH,
            status=Task.Status.PENDING,
            due_date=timezone.now() + timedelta(days=2),
        )

    def test_task_list_requires_login(self):
        response = self.client.get(
            reverse("recruitment:task_list")
        )

        self.assertEqual(response.status_code, 302)

    def test_user_sees_only_own_tasks(self):
        self.client.login(
            username="candidata1",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse("recruitment:task_list")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Llamar a una empresa",
        )

        self.assertNotContains(
            response,
            "Preparar una entrevista",
        )

    def test_user_cannot_access_another_users_task(self):
        self.client.login(
            username="candidata1",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse(
                "recruitment:task_detail",
                kwargs={"pk": self.task2.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_created_task_belongs_to_logged_in_user(self):
        self.client.login(
            username="candidata1",
            password="TestPassword123!",
        )

        due_date = timezone.localtime(
            timezone.now() + timedelta(days=3)
        ).strftime("%Y-%m-%dT%H:%M")

        response = self.client.post(
            reverse("recruitment:task_create"),
            {
                "title": "Nueva tarea de prueba",
                "description": "Tarea creada durante el test",
                "task_type": Task.TaskType.OTHER,
                "priority": Task.Priority.MEDIUM,
                "status": Task.Status.PENDING,
                "due_date": due_date,
            },
        )

        self.assertEqual(response.status_code, 302)

        task = Task.objects.get(
            title="Nueva tarea de prueba"
        )

        self.assertEqual(task.owner, self.user1)

    def test_user_cannot_complete_another_users_task(self):
        self.client.login(
            username="candidata1",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse(
                "recruitment:task_complete",
                kwargs={"pk": self.task2.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.task2.refresh_from_db()

        self.assertEqual(
            self.task2.status,
            Task.Status.PENDING,
        )

    
class TaskOverdueAndCompletionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="hu11user",
            email="hu11@example.com",
            password="TestPassword123!",
        )
        self.client.login(
            username="hu11user",
            password="TestPassword123!",
        )
        self.task = Task.objects.create(
            owner=self.user,
            title="Tarea HU11",
            status=Task.Status.PENDING,
            due_date=timezone.now() - timedelta(hours=1),
        )

    def test_task_is_overdue_when_past_due_and_not_completed(self):
        self.assertTrue(self.task.is_overdue)

    def test_task_is_not_overdue_when_due_date_is_future(self):
        self.task.due_date = timezone.now() + timedelta(days=1)
        self.assertFalse(self.task.is_overdue)

    def test_completed_task_is_not_overdue(self):
        self.task.status = Task.Status.COMPLETED
        self.task.completed_at = timezone.now()
        self.task.save()

        self.assertFalse(self.task.is_overdue)

    def test_overdue_task_is_highlighted_in_list(self):
        response = self.client.get(reverse("recruitment:task_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="task-overdue"')
        self.assertContains(response, "Tarea vencida")

    def test_completing_task_sets_completed_at(self):
        response = self.client.post(
            reverse("recruitment:task_complete", args=[self.task.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.COMPLETED)
        self.assertIsNotNone(self.task.completed_at)

    def test_reopening_task_clears_completed_at(self):
        self.task.status = Task.Status.COMPLETED
        self.task.completed_at = timezone.now()
        self.task.save()

        response = self.client.post(
            reverse("recruitment:task_reopen", args=[self.task.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.PENDING)
        self.assertIsNone(self.task.completed_at)

    def test_editing_task_to_completed_sets_completed_at(self):
        due_date = timezone.localtime(
            self.task.due_date
        ).strftime("%Y-%m-%dT%H:%M")

        response = self.client.post(
            reverse("recruitment:task_update", args=[self.task.pk]),
            {
                "title": self.task.title,
                "description": "",
                "task_type": self.task.task_type,
                "priority": self.task.priority,
                "status": Task.Status.COMPLETED,
                "due_date": due_date,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.COMPLETED)
        self.assertIsNotNone(self.task.completed_at)

    def test_editing_completed_task_to_pending_clears_completed_at(self):
        self.task.status = Task.Status.COMPLETED
        self.task.completed_at = timezone.now()
        self.task.save()

        due_date = timezone.localtime(
            self.task.due_date
        ).strftime("%Y-%m-%dT%H:%M")

        response = self.client.post(
            reverse("recruitment:task_update", args=[self.task.pk]),
            {
                "title": self.task.title,
                "description": "",
                "task_type": self.task.task_type,
                "priority": self.task.priority,
                "status": Task.Status.PENDING,
                "due_date": due_date,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.PENDING)
        self.assertIsNone(self.task.completed_at)