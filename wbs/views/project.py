from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime
from ..models import Project
from ..forms import ProjectForm, TaskForm

@login_required
def project_list(request):
    base_queryset = Project.objects.filter(owner=request.user)
    
    # 프로젝트 통계 계산
    completed_projects = base_queryset.filter(progress=100).count()
    in_progress_projects = base_queryset.filter(Q(progress__gt=0) & Q(progress__lt=100)).count()
    not_started_projects = base_queryset.filter(progress=0).count()
    
    # 상태별 필터링
    status = request.GET.get('status')
    if status == 'completed':
        projects = base_queryset.filter(progress=100)
        active_filter = 'completed'
    elif status == 'in_progress':
        projects = base_queryset.filter(Q(progress__gt=0) & Q(progress__lt=100))
        active_filter = 'in_progress'
    elif status == 'not_started':
        projects = base_queryset.filter(progress=0)
        active_filter = 'not_started'
    else:
        projects = base_queryset
        active_filter = 'all'
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project created successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'wbs/project/project_list.html', {
        'projects': projects,
        'form': form,
        'completed_projects': completed_projects,
        'in_progress_projects': in_progress_projects,
        'not_started_projects': not_started_projects,
        'active_filter': active_filter
    })

# JSON 직렬화를 위한 커스텀 인코더
class TaskJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)

@login_required
def project_detail(request, pk):
    """프로젝트 상세 정보 표시 및 수정"""
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    # 모든 태스크 가져오기
    all_tasks = project.tasks.all()
    # 최상위 태스크 (부모가 없는 태스크)
    root_tasks = project.tasks.filter(parent=None)
    
    # Get task counts
    completed_tasks_count = project.tasks.filter(status='completed').count()
    blocked_tasks_count = project.tasks.filter(status='blocked').count()
    
    if request.method == 'POST':
        if 'edit_project' in request.POST:
            project_form = ProjectForm(request.POST, instance=project)
            if project_form.is_valid():
                project_form.save()
                messages.success(request, 'Project updated successfully.')
                return redirect('project_detail', pk=project.pk)
        else:
            form = TaskForm(project, request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.project = project
                # order 값 설정 - 현재 최대 순서 + 1
                max_order = project.tasks.all().order_by('-order').first()
                task.order = max_order.order + 1 if max_order else 0
                task.save()
                messages.success(request, 'Task created successfully.')
                return redirect('project_detail', pk=project.pk)
    else:
        form = TaskForm(project)
        project_form = ProjectForm(instance=project)
    
    # 간트 차트를 위한 태스크 데이터 JSON 직렬화
    tasks_data = []
    for task in all_tasks:
        # 시작일이나 종료일이 없는 경우 빈 데이터 대신 기본값 사용
        start_date = task.start_date.strftime('%Y-%m-%d') if task.start_date else None
        end_date = task.end_date.strftime('%Y-%m-%d') if task.end_date else None
        
        # 시작일이 없으면 프로젝트 시작일 또는 오늘 날짜로 기본값 설정
        if not start_date and task.end_date:
            from datetime import timedelta
            temp_start = task.end_date - timedelta(days=3)
            start_date = temp_start.strftime('%Y-%m-%d')
        
        # 종료일이 없으면 프로젝트 종료일 또는 시작일 + 3일로 기본값 설정
        if not end_date and task.start_date:
            from datetime import timedelta
            temp_end = task.start_date + timedelta(days=3)
            end_date = temp_end.strftime('%Y-%m-%d')
        
        # 시작일과 종료일 모두 없으면 표시하지 않음
        if not start_date and not end_date:
            continue
        
        task_data = {
            'id': task.pk,
            'title': task.title,
            'startDate': start_date,
            'endDate': end_date,
            'progress': task.progress,
            'status': task.status,
            'parentId': task.parent.pk if task.parent else None
        }
        tasks_data.append(task_data)
    
    # 가장 단순한 방식으로 JSON 처리
    tasks_json = json.dumps(tasks_data, ensure_ascii=False)
    
    return render(request, 'wbs/project/project_detail.html', {
        'project': project,
        'tasks': all_tasks,  # 모든 태스크 전달
        'root_tasks': root_tasks,  # 최상위 태스크 전달 
        'form': form,
        'project_form': project_form,
        'completed_tasks_count': completed_tasks_count,
        'blocked_tasks_count': blocked_tasks_count,
        'tasks_json': tasks_json,  # 간트 차트용 JSON 데이터
    })

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('project_list')
    
    return render(request, 'wbs/project/project_confirm_delete.html', {
        'project': project,
    }) 