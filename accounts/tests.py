from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

PASSWORD = "PruebaSegura123!"


class AccountsTests(TestCase):
    def test_register_page_is_accessible(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear cuenta")
        self.assertContains(response, "Registrarme")

    def test_user_can_register(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "usuario_prueba",
                "email": "prueba@example.com",
                "first_name": "Usuario",
                "last_name": "Prueba",
                "role": "candidate",
                "professional_title": "Desarrollador",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="usuario_prueba")
        self.assertEqual(user.email, "prueba@example.com")
        self.assertEqual(user.professional_title, "Desarrollador")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile_edit"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_logged_in_user_can_update_profile(self):
        user = User.objects.create_user(
            username="perfil_prueba",
            email="perfil@example.com",
            password=PASSWORD,
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:profile_edit"),
            {
                "first_name": "María",
                "last_name": "García",
                "email": "perfil@example.com",
                "professional_title": "Diseñadora UX",
                "phone": "+34 600 000 000",
                "city": "Barcelona",
                "bio": "Experiencia en diseño de productos digitales.",
            },
        )

        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()
        self.assertEqual(user.first_name, "María")
        self.assertEqual(user.professional_title, "Diseñadora UX")
        self.assertEqual(user.city, "Barcelona")
        self.assertEqual(user.bio, "Experiencia en diseño de productos digitales.")

    def test_user_can_log_in(self):
        User.objects.create_user(
            username="login_prueba",
            email="login@example.com",
            password=PASSWORD,
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "login_prueba", "password": PASSWORD},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_user_can_log_out(self):
        user = User.objects.create_user(
            username="logout_prueba",
            email="logout@example.com",
            password=PASSWORD,
        )
        self.client.force_login(user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_register_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(
            username="usuario_existente",
            email="Prueba@example.com",
            password=PASSWORD,
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "usuario_nuevo",
                "email": "prueba@EXAMPLE.com",
                "role": "candidate",
                "password1": "OtraClaveSegura123!",
                "password2": "OtraClaveSegura123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="usuario_nuevo").exists())
        self.assertContains(
            response,
            "Ya existe una cuenta con este correo electrónico.",
        )

    def test_profile_rejects_another_users_email(self):
        User.objects.create_user(
            username="otro_usuario",
            email="otro@example.com",
            password=PASSWORD,
        )
        usuario = User.objects.create_user(
            username="usuario_perfil",
            email="propio@example.com",
            password=PASSWORD,
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("accounts:profile_edit"),
            {
                "first_name": "Usuario",
                "last_name": "Perfil",
                "email": "OTRO@example.com",
                "bio": "Mi biografía",
            },
        )

        self.assertEqual(response.status_code, 200)

        usuario.refresh_from_db()
        self.assertEqual(usuario.email, "propio@example.com")
        self.assertContains(
            response,
            "Ya existe una cuenta con este correo electrónico.",
        )