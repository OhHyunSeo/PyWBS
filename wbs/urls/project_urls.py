from django.urls import path
from ..views import project_list, project_detail, project_delete

urlpatterns = [
    path('', project_list, name='project_list'),
    path('<int:pk>/', project_detail, name='project_detail'),
    path('<int:pk>/delete/', project_delete, name='project_delete'),
] 