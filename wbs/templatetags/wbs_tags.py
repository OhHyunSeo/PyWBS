from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def progress_bar(value, height='0.5rem', bg_class='bg-primary'):
    """진행률 표시 바를 렌더링합니다."""
    html = f'''
    <div class="progress" style="height: {height};">
        <div class="progress-bar {bg_class}" 
             role="progressbar" 
             style="width: {value}%;" 
             aria-valuenow="{value}" 
             aria-valuemin="0" 
             aria-valuemax="100">
        </div>
    </div>
    '''
    return mark_safe(html)

@register.simple_tag
def status_badge(status):
    """상태에 따른 배지를 렌더링합니다."""
    status_classes = {
        'not_started': 'bg-secondary',
        'in_progress': 'bg-warning',
        'completed': 'bg-success',
        'blocked': 'bg-danger'
    }
    
    status_labels = {
        'not_started': 'Not Started',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'blocked': 'Blocked'
    }
    
    css_class = status_classes.get(status, 'bg-secondary')
    label = status_labels.get(status, status)
    
    html = f'<span class="badge {css_class}">{label}</span>'
    return mark_safe(html)

@register.filter
def get_item(dictionary, key):
    """딕셔너리에서 키를 사용하여 값을 가져옵니다."""
    return dictionary.get(key)

@register.filter
def task_count(tasks, status):
    """지정된 상태의 태스크 수를 반환합니다."""
    return tasks.filter(status=status).count()

@register.inclusion_tag('wbs/components/task_card.html')
def render_task_card(task):
    """태스크 카드를 렌더링합니다."""
    return {'task': task} 