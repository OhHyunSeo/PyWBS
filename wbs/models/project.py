from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .base import TimeStampedModel

User = get_user_model()

class Project(TimeStampedModel):
    """
    프로젝트 모델
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    progress = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    def calculate_progress(self):
        """
        모든 태스크의 진행률을 기반으로 프로젝트 진행률을 계산
        """
        tasks = self.tasks.all()
        if not tasks:
            return 0
        
        total_progress = sum(task.progress for task in tasks)
        return int(total_progress / tasks.count())
    
    def update_progress(self):
        """
        프로젝트 진행률을 계산하고 저장
        """
        self.progress = self.calculate_progress()
        self.save(update_fields=['progress', 'updated_at'])
        
    def get_status(self):
        """
        프로젝트 상태 반환
        """
        if self.progress == 0:
            return 'not_started'
        elif self.progress == 100:
            return 'completed'
        else:
            return 'in_progress'
            
    def get_status_display(self):
        """
        프로젝트 상태의 사용자 친화적 표시 반환
        """
        status = self.get_status()
        status_map = {
            'not_started': 'Not Started',
            'in_progress': 'In Progress',
            'completed': 'Completed'
        }
        return status_map.get(status, status)

    def save(self, *args, **kwargs):
        if not self.pk:  # 새로운 프로젝트인 경우
            super().save(*args, **kwargs)  # 먼저 저장하여 pk를 생성
        self.progress = self.calculate_progress()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at'] 