from django.urls import path
from ..views import edit_comment, delete_comment

urlpatterns = [
    path('project/<int:project_pk>/task/<int:task_pk>/comment/<int:comment_pk>/edit/', edit_comment, name='edit_comment'),
    path('project/<int:project_pk>/task/<int:task_pk>/comment/<int:comment_pk>/delete/', delete_comment, name='delete_comment'),
] 