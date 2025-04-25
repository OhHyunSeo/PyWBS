from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from ..models import Project, Task

@login_required
def dashboard(request):
    """
    Notion 스타일의 통합 대시보드 제공
    """
    # 사용자의 모든 프로젝트
    projects = Project.objects.filter(owner=request.user)
    
    # 최근에 업데이트된 프로젝트
    recent_projects = projects.order_by('-updated_at')[:5]
    
    # 마감일이 가까운 태스크 (2주 이내)
    from django.utils import timezone
    from datetime import timedelta
    two_weeks_later = timezone.now() + timedelta(days=14)
    upcoming_tasks = Task.objects.filter(
        project__in=projects,
        end_date__lte=two_weeks_later,
        end_date__gte=timezone.now(),
        status__in=['not_started', 'in_progress']
    ).order_by('end_date')[:5]
    
    # 프로젝트 상태 통계
    completed_projects = projects.filter(progress=100).count()
    in_progress_projects = projects.filter(Q(progress__gt=0) & Q(progress__lt=100)).count()
    not_started_projects = projects.filter(progress=0).count()
    
    # 태스크 상태 통계
    all_tasks = Task.objects.filter(project__in=projects)
    task_stats = {
        'total': all_tasks.count(),
        'completed': all_tasks.filter(status='completed').count(),
        'in_progress': all_tasks.filter(status='in_progress').count(),
        'not_started': all_tasks.filter(status='not_started').count(),
        'blocked': all_tasks.filter(status='blocked').count(),
    }
    
    # 상태별 태스크 목록 (최근 5개)
    recent_completed_tasks = all_tasks.filter(status='completed').order_by('-updated_at')[:5]
    recent_blocked_tasks = all_tasks.filter(status='blocked').order_by('-updated_at')[:5]
    
    # 배정된 태스크 (현재 사용자에게)
    my_tasks = all_tasks.filter(assignee=request.user).order_by('end_date')
    
    return render(request, 'wbs/dashboard.html', {
        'recent_projects': recent_projects,
        'upcoming_tasks': upcoming_tasks,
        'project_stats': {
            'total': projects.count(),
            'completed': completed_projects,
            'in_progress': in_progress_projects,
            'not_started': not_started_projects,
        },
        'task_stats': task_stats,
        'recent_completed_tasks': recent_completed_tasks,
        'recent_blocked_tasks': recent_blocked_tasks,
        'my_tasks': my_tasks,
    }) 