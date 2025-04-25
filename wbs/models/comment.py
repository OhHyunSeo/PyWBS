from django.db import models
from django.contrib.auth import get_user_model
from .base import TimeStampedModel

User = get_user_model()

class Comment(TimeStampedModel):
    """댓글 모델"""
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'Comment by {self.author.username} on {self.task.title}'

    class Meta:
        ordering = ['-created_at'] 