from django.db import models

class TimeStampedModel(models.Model):
    """
    생성 및 수정 시간 필드를 포함하는 추상 기본 모델
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 