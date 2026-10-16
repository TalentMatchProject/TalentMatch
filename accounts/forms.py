from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User

class UniqueEmailMixin:
    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        users = User.objects.filter(email__iexact=email)

        if self.instance.pk:
            users = users.exclude(pk=self.instance.pk)

        if users.exists():
            raise forms.ValidationError(
                "Ya existe una cuenta con este correo electrónico."
            )

        return email


class CustomUserCreationForm(UniqueEmailMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "professional_title",
            "phone",
            "city",
        )


class CustomUserUpdateForm(UniqueEmailMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "professional_title",
            "phone",
            "city",
            "bio",
            "avatar",
        )
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}