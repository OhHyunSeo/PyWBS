from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .base import TimeStampedModel

User = get_user_model()

class Task(TimeStampedModel):
    """태스크 모델"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='tasks')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress = models.PositiveIntegerField(default=0)  # 0-100
    order = models.IntegerField(default=0)  # 태스크 정렬 순서
    
    def __str__(self):
        return self.title
    
    def update_status_based_on_progress(self):
        """진행률에 따라 상태 자동 업데이트"""
        if self.progress == 0:
            self.status = 'not_started'
        elif self.progress == 100:
            self.status = 'completed'
        elif self.status not in ['blocked', 'in_progress']:
            self.status = 'in_progress'
            
    def update_parent_progress(self):
        """부모 태스크의 진행률 업데이트"""
        if self.parent:
            # 부모의 모든 하위 태스크의 평균 진행률 계산
            subtasks = self.parent.subtasks.all()
            if subtasks.count() > 0:  # 0으로 나누기 방지
                total_progress = sum(task.progress for task in subtasks)
                self.parent.progress = total_progress // subtasks.count()
                self.parent.save(update_fields=['progress'])
            
    def save(self, *args, **kwargs):
        # 진행률에 따라 상태 자동 업데이트
        self.update_status_based_on_progress()
        
        # 저장
        super().save(*args, **kwargs)
        
        # 부모 태스크 진행률 업데이트
        self.update_parent_progress()
        
        # 프로젝트 진행률 업데이트
        self.project.update_progress()
        
    class Meta:
        ordering = ['start_date', 'title'] 