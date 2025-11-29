from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance', 'dependencies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskAnalysisInputSerializer(serializers.Serializer):
    """Serializer for task analysis input."""
    tasks = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="List of task objects to analyze"
    )
    profile = serializers.ChoiceField(
        choices=['fastest_wins', 'high_impact', 'deadline_driven', 'smart_balance'],
        default='smart_balance',
        required=False,
        help_text="Scoring profile to use"
    )


class ScoredTaskSerializer(serializers.Serializer):
    """Serializer for scored task output."""
    id = serializers.IntegerField()
    title = serializers.CharField()
    due_date = serializers.DateField()
    estimated_hours = serializers.IntegerField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    score = serializers.FloatField()
    breakdown = serializers.DictField()
    explanation = serializers.CharField()
    is_overdue = serializers.BooleanField()
    overdue_days = serializers.IntegerField()


class TaskAnalysisOutputSerializer(serializers.Serializer):
    """Serializer for task analysis output."""
    tasks = ScoredTaskSerializer(many=True)
    profile = serializers.CharField()
    errors = serializers.ListField(child=serializers.CharField(), allow_empty=True)




