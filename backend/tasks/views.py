from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import date
import json

from .scoring import ScoringEngine
from .serializers import (
    TaskAnalysisInputSerializer,
    TaskAnalysisOutputSerializer,
    TaskSerializer
)
from .models import Task


@api_view(['POST'])
def analyze_tasks(request):
    """
    Analyze and score a list of tasks.
    
    Expected input:
    {
        "tasks": [
            {
                "id": 1,
                "title": "Task name",
                "due_date": "2024-12-31",
                "estimated_hours": 4,
                "importance": 7,
                "dependencies": [2, 3]
            },
            ...
        ],
        "profile": "smart_balance"  # optional
    }
    
    Returns sorted tasks with scores and explanations.
    """
    serializer = TaskAnalysisInputSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid input', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    tasks = serializer.validated_data['tasks']
    profile = serializer.validated_data.get('profile', 'smart_balance')
    
    # Validate task structure
    required_fields = ['title', 'due_date', 'estimated_hours', 'importance']
    for i, task in enumerate(tasks):
        missing = [field for field in required_fields if field not in task]
        if missing:
            return Response(
                {
                    'error': f'Task at index {i} is missing required fields',
                    'missing_fields': missing
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate due_date format
        try:
            if isinstance(task['due_date'], str):
                date.fromisoformat(task['due_date'])
        except (ValueError, TypeError):
            return Response(
                {
                    'error': f'Task "{task.get("title", i)}" has invalid due_date format. Use YYYY-MM-DD.',
                    'received': task['due_date']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate estimated_hours
        if not isinstance(task['estimated_hours'], int) or task['estimated_hours'] < 0:
            return Response(
                {
                    'error': f'Task "{task.get("title", i)}" has invalid estimated_hours. Must be non-negative integer.',
                    'received': task['estimated_hours']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate importance
        if not isinstance(task['importance'], int) or not (1 <= task['importance'] <= 10):
            return Response(
                {
                    'error': f'Task "{task.get("title", i)}" has invalid importance. Must be integer between 1 and 10.',
                    'received': task['importance']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate dependencies
        if 'dependencies' in task:
            if not isinstance(task['dependencies'], list):
                return Response(
                    {
                        'error': f'Task "{task.get("title", i)}" has invalid dependencies. Must be a list.',
                        'received': task['dependencies']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Ensure all dependencies are integers
            for dep in task['dependencies']:
                if not isinstance(dep, int):
                    return Response(
                        {
                            'error': f'Task "{task.get("title", i)}" has invalid dependency. All dependencies must be integers.',
                            'received': dep
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            task['dependencies'] = []
    
    # Run analysis
    try:
        engine = ScoringEngine(profile=profile)
        result = engine.analyze_tasks(tasks, profile=profile)
        
        # If there are errors from scoring, return them
        if result.get('errors'):
            return Response(
                {
                    'error': 'Scoring errors occurred',
                    'details': result['errors']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        output_serializer = TaskAnalysisOutputSerializer(data=result)
        if output_serializer.is_valid():
            return Response(output_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to serialize output', 'details': output_serializer.errors},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def suggest_tasks(request):
    """
    Get top 3 task suggestions from database.
    Returns tasks sorted by score with explanations.
    """
    try:
        # Get all tasks from database
        tasks = Task.objects.all()
        
        if not tasks.exists():
            return Response(
                {
                    'suggestions': [],
                    'message': 'No tasks found in database. Add tasks via admin or API.'
                },
                status=status.HTTP_200_OK
            )
        
        # Convert to dict format for scoring
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date.isoformat(),
                'estimated_hours': task.estimated_hours,
                'importance': task.importance,
                'dependencies': task.dependencies if task.dependencies else [],
            })
        
        # Get profile from query params
        profile = request.query_params.get('profile', 'smart_balance')
        
        # Score tasks
        engine = ScoringEngine(profile=profile)
        result = engine.analyze_tasks(task_list, profile=profile)
        
        if result.get('errors'):
            return Response(
                {
                    'error': 'Error analyzing tasks',
                    'details': result['errors']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get top 3
        top_tasks = result['tasks'][:3]
        
        # Generate summary explanation
        if top_tasks:
            explanations = []
            for i, task in enumerate(top_tasks, 1):
                explanations.append(f"{i}. {task['title']}: {task['explanation']}")
            summary = " ".join(explanations)
        else:
            summary = "No tasks available for suggestions."
        
        return Response(
            {
                'suggestions': top_tasks,
                'summary': summary,
                'profile': result['profile']
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




