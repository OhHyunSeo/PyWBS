from rest_framework import serializers
from .models import Project, Task, Comment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['author']

class TaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['project']

    def get_subtasks(self, obj):
        subtasks = Task.objects.filter(parent=obj)
        return TaskSerializer(subtasks, many=True).data

class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['owner'] 