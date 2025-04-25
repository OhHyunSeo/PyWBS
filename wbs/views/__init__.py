from .auth import SignUpView
from .dashboard import dashboard
from .project import project_list, project_detail, project_delete
from .task import task_detail, task_delete, update_task_progress, task_list, edit_comment, delete_comment

__all__ = [
    'SignUpView',
    'dashboard',
    'project_list', 
    'project_detail', 
    'project_delete',
    'task_list',
    'task_detail', 
    'task_delete', 
    'update_task_progress',
    'edit_comment',
    'delete_comment'
] 