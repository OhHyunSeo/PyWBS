from django import forms
from django.contrib.auth import get_user_model
from ..models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'start_date', 'end_date', 'status', 'parent', 'order']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'order': forms.HiddenInput(),  # 사용자에게 노출하지 않음
        }

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = project.tasks.all()
        self.fields['assignee'].queryset = get_user_model().objects.all()
        if not self.instance.pk:  # 새로운 태스크인 경우
            self.fields['parent'].required = False
            self.fields['order'].required = False  # order는 view에서 설정하므로 required=False 