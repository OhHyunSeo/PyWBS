from django.urls import path
from ..views import task_list, task_detail, task_delete, update_task_progress

urlpatterns = [
    path('', task_list, name='task_list'),
    path('project/<int:project_pk>/task/<int:pk>/', task_detail, name='task_detail'),
    path('project/<int:project_pk>/task/<int:pk>/delete/', task_delete, name='task_delete'),
    path('project/<int:project_pk>/task/<int:pk>/update-progress/', update_task_progress, name='update_task_progress'),
] 