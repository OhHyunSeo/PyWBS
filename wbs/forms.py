from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Task, Comment

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'start_date', 'end_date', 'status', 'parent']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = project.tasks.all()
        self.fields['assignee'].queryset = get_user_model().objects.all()
        if not self.instance.pk:  # 새로운 태스크인 경우
            self.fields['parent'].required = False
            self.fields['parent'].initial = None  # 명시적으로 None으로 설정
            self.initial['parent'] = None  # 초기값도 None으로 설정

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        } 