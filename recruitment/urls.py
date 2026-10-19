from django.urls import path

from . import views

app_name = "recruitment"

urlpatterns = [
    path("", views.task_list, name="task_list"),
    path("create/", views.task_create, name="task_create"),
    path("<int:pk>/", views.task_detail, name="task_detail"),
    path("<int:pk>/edit/", views.task_update, name="task_update"),
    path("<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("<int:pk>/complete/", views.task_complete, name="task_complete"),
    path("<int:pk>/reopen/", views.task_reopen, name="task_reopen"),
]