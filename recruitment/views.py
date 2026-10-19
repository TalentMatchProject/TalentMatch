from django.http import HttpResponse


def task_list(request):
    return HttpResponse("Página de tareas")