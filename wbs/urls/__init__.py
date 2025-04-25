# URL 정의 파일
from django.urls import path, include
from ..views import dashboard
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('project_list')

# 기능별 URL 패턴 가져오기
from .project_urls import urlpatterns as project_urls
from .task_urls import urlpatterns as task_urls
from .comment_urls import urlpatterns as comment_urls
from .auth_urls import urlpatterns as auth_urls

# 모든 URL 패턴 통합
urlpatterns = [
    path('', dashboard, name='dashboard'),  # 대시보드를 홈페이지로 설정
    path('logout/', logout_view, name='custom_logout'),
    path('projects/', include(project_urls)),
    path('tasks/', include(task_urls)),
    path('comments/', include(comment_urls)),
    path('auth/', include(auth_urls)),
] 