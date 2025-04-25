from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import json
from ..models import Project, Task, Comment
from ..forms import TaskForm, CommentForm

@login_required
def task_list(request):
    """사용자의 모든 태스크 목록을 표시"""
    # 사용자가 소유한 프로젝트의 태스크만 표시
    projects = Project.objects.filter(owner=request.user)
    
    # 모든 태스크(필터링 전)
    all_tasks = Task.objects.filter(project__in=projects)
    
    # 상태별 필터링
    status = request.GET.get('status')
    if status in ['not_started', 'in_progress', 'completed', 'blocked']:
        tasks = all_tasks.filter(status=status)
        active_filter = status
    else:
        tasks = all_tasks
        active_filter = 'all'
    
    # 담당자별 필터링
    assignee = request.GET.get('assignee')
    if assignee == 'me':
        tasks = tasks.filter(assignee=request.user)
    elif assignee == 'unassigned':
        tasks = tasks.filter(assignee=None)
    
    # 통계 계산 (항상 모든 태스크로 계산)
    not_started = all_tasks.filter(status='not_started').count()
    in_progress = all_tasks.filter(status='in_progress').count()
    completed = all_tasks.filter(status='completed').count()
    blocked = all_tasks.filter(status='blocked').count()
    
    context = {
        'tasks': tasks,
        'active_filter': active_filter,
        'not_started_tasks': not_started,
        'in_progress_tasks': in_progress,
        'completed_tasks': completed,
        'blocked_tasks': blocked,
    }
    
    return render(request, 'wbs/task/task_list.html', context)

@login_required
def task_detail(request, project_pk, pk):
    """태스크 상세 정보 표시 및 수정"""
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    task = get_object_or_404(Task, pk=pk, project=project)
    comments = task.comments.all()
    
    if request.method == 'POST':
        if 'update_task' in request.POST:
            form = TaskForm(project, request.POST, instance=task)
            if form.is_valid():
                form.save()
                messages.success(request, 'Task updated successfully.')
                return redirect('task_detail', project_pk=project.pk, pk=task.pk)
        elif 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.author = request.user
                comment.save()
                messages.success(request, 'Comment added successfully.')
                return redirect('task_detail', project_pk=project.pk, pk=task.pk)
    else:
        form = TaskForm(project, instance=task)
        comment_form = CommentForm()
    
    return render(request, 'wbs/task/task_detail.html', {
        'project': project,
        'task': task,
        'comments': comments,
        'form': form,
        'comment_form': comment_form,
    })

@login_required
def task_delete(request, project_pk, pk):
    """태스크 삭제"""
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    task = get_object_or_404(Task, pk=pk, project=project)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('project_detail', pk=project.pk)
    
    return render(request, 'wbs/task/task_confirm_delete.html', {
        'project': project,
        'task': task,
    })

@login_required
def update_task_progress(request, project_pk, pk):
    """태스크 진행률 업데이트"""
    task = get_object_or_404(Task, pk=pk, project__pk=project_pk)
    if request.method == 'POST':
        # JSON 요청인지 확인
        if request.content_type == 'application/json':
            import json
            try:
                data = json.loads(request.body)
                progress = data.get('progress')
                if progress is not None:
                    try:
                        progress = int(progress)
                        if 0 <= progress <= 100:
                            task.progress = progress
                            task.save()
                            return JsonResponse({
                                'success': True,
                                'progress': progress,
                                'status': task.status
                            })
                        else:
                            return JsonResponse({
                                'success': False,
                                'error': 'Progress must be between 0 and 100.'
                            })
                    except ValueError:
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid progress value.'
                        })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Progress value is required.'
                    })
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data.'
                })
        # 일반 폼 제출 처리 (기존 코드)
        else:
            progress = request.POST.get('progress')
            if progress is not None:
                try:
                    progress = int(progress)
                    if 0 <= progress <= 100:
                        task.progress = progress
                        task.save()
                        messages.success(request, 'Task progress updated successfully.')
                    else:
                        messages.error(request, 'Progress must be between 0 and 100.')
                except ValueError:
                    messages.error(request, 'Invalid progress value.')
            else:
                messages.error(request, 'Progress value is required.')
    return redirect('task_detail', project_pk=project_pk, pk=pk)

@login_required
def edit_comment(request, project_pk, task_pk, comment_pk):
    """댓글 수정"""
    project = get_object_or_404(Project, pk=project_pk)
    task = get_object_or_404(Task, pk=task_pk, project=project)
    comment = get_object_or_404(Comment, pk=comment_pk, task=task)
    
    # 댓글 작성자만 수정 가능
    if comment.author != request.user:
        messages.error(request, 'You do not have permission to edit this comment.')
        return redirect('task_detail', project_pk=project_pk, pk=task_pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully.')
            return redirect('task_detail', project_pk=project_pk, pk=task_pk)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'wbs/comment/edit_comment.html', {
        'form': form,
        'project': project,
        'task': task,
        'comment': comment
    })

@login_required
def delete_comment(request, project_pk, task_pk, comment_pk):
    """댓글 삭제"""
    project = get_object_or_404(Project, pk=project_pk)
    task = get_object_or_404(Task, pk=task_pk, project=project)
    comment = get_object_or_404(Comment, pk=comment_pk, task=task)
    
    # 댓글 작성자만 삭제 가능
    if comment.author != request.user:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('task_detail', project_pk=project_pk, pk=task_pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('task_detail', project_pk=project_pk, pk=task_pk)
    
    return render(request, 'wbs/comment/comment_confirm_delete.html', {
        'project': project,
        'task': task,
        'comment': comment
    }) 