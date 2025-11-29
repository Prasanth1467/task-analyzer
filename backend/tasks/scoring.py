"""
Smart Task Scoring Engine

This module implements a sophisticated scoring algorithm that prioritizes tasks
based on multiple factors including urgency, importance, effort, and dependencies.
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from collections import deque


class ScoringEngine:
    """Main scoring engine with configurable weighting profiles."""
    
    # Weighting profiles
    PROFILES = {
        'fastest_wins': {
            'urgency_weight': 0.2,
            'importance_weight': 0.1,
            'effort_weight': 0.6,  # Negative - lower effort = higher score
            'dependency_weight': 0.1,
            'overdue_multiplier': 2.0,
        },
        'high_impact': {
            'urgency_weight': 0.2,
            'importance_weight': 0.5,
            'effort_weight': 0.1,
            'dependency_weight': 0.2,
            'overdue_multiplier': 2.5,
        },
        'deadline_driven': {
            'urgency_weight': 0.6,
            'importance_weight': 0.2,
            'effort_weight': 0.1,
            'dependency_weight': 0.1,
            'overdue_multiplier': 3.0,
        },
        'smart_balance': {
            'urgency_weight': 0.35,
            'importance_weight': 0.3,
            'effort_weight': 0.2,
            'dependency_weight': 0.15,
            'overdue_multiplier': 2.5,
        },
    }

    def __init__(self, profile: str = 'smart_balance'):
        """Initialize scoring engine with a specific profile."""
        if profile not in self.PROFILES:
            raise ValueError(f"Unknown profile: {profile}. Choose from {list(self.PROFILES.keys())}")
        
        self.profile = profile
        self.weights = self.PROFILES[profile]

    def detect_circular_dependencies(self, tasks: List[Dict[str, Any]]) -> Optional[List[int]]:
        """
        Detect circular dependencies using DFS.
        Returns a list of task IDs involved in a cycle if found, None otherwise.
        """
        # Build adjacency list
        task_map = {task['id']: task for task in tasks}
        graph = {task['id']: task.get('dependencies', []) for task in tasks}
        
        # Check all nodes
        for task_id in graph:
            visited = set()
            rec_stack = set()
            
            def dfs(node):
                if node in rec_stack:
                    return [node]  # Found cycle
                if node in visited:
                    return None
                
                visited.add(node)
                rec_stack.add(node)
                
                for dep in graph.get(node, []):
                    if dep not in task_map:
                        continue  # Skip invalid dependencies
                    result = dfs(dep)
                    if result:
                        if node not in result:
                            result.append(node)
                        return result
                
                rec_stack.remove(node)
                return None
            
            cycle = dfs(task_id)
            if cycle:
                return cycle
        
        return None

    def calculate_urgency_score(self, due_date: date, today: date = None) -> float:
        """Calculate urgency based on days until due date."""
        if today is None:
            today = date.today()
        
        days_until = (due_date - today).days
        
        if days_until < 0:
            # Overdue - return high negative value (will be handled separately)
            return -abs(days_until) * 10
        elif days_until == 0:
            return 100.0  # Due today
        elif days_until <= 1:
            return 90.0
        elif days_until <= 3:
            return 70.0
        elif days_until <= 7:
            return 50.0
        elif days_until <= 14:
            return 30.0
        elif days_until <= 30:
            return 15.0
        else:
            return max(5.0, 30.0 - (days_until - 30) * 0.5)

    def calculate_importance_score(self, importance: int) -> float:
        """Normalize importance (1-10) to 0-100 scale."""
        if not (1 <= importance <= 10):
            raise ValueError(f"Importance must be between 1 and 10, got {importance}")
        return (importance / 10.0) * 100.0

    def calculate_effort_score(self, estimated_hours: int) -> float:
        """Calculate effort score (lower effort = higher score for quick wins)."""
        if estimated_hours < 0:
            raise ValueError(f"Estimated hours cannot be negative, got {estimated_hours}")
        
        if estimated_hours == 0:
            return 100.0  # Instant task
        
        # Inverse relationship: lower hours = higher score
        if estimated_hours <= 1:
            return 100.0
        elif estimated_hours <= 2:
            return 80.0
        elif estimated_hours <= 4:
            return 60.0
        elif estimated_hours <= 8:
            return 40.0
        elif estimated_hours <= 16:
            return 20.0
        else:
            return max(5.0, 30.0 - (estimated_hours - 16) * 0.5)

    def calculate_dependency_score(self, task: Dict[str, Any], tasks: List[Dict[str, Any]]) -> float:
        """Calculate score boost based on dependency count and blocking status."""
        dependencies = task.get('dependencies', [])
        task_map = {t['id']: t for t in tasks}
        
        if not dependencies:
            return 50.0  # No dependencies - neutral score
        
        # Count how many tasks depend on this one (blocking score)
        blocking_count = sum(1 for t in tasks if task['id'] in t.get('dependencies', []))
        
        # Tasks with many dependents get priority boost
        blocking_score = min(100.0, 50.0 + blocking_count * 10.0)
        
        # Tasks with fewer dependencies get slight boost (can start sooner)
        dependency_count_score = max(30.0, 70.0 - len(dependencies) * 5.0)
        
        # Weighted combination
        return (blocking_score * 0.6) + (dependency_count_score * 0.4)

    def score_task(self, task: Dict[str, Any], tasks: List[Dict[str, Any]], today: date = None) -> Dict[str, Any]:
        """
        Calculate comprehensive score for a single task.
        Returns dict with score, breakdown, and explanation.
        """
        if today is None:
            today = date.today()
        
        # Validate required fields
        required_fields = ['title', 'due_date', 'estimated_hours', 'importance']
        for field in required_fields:
            if field not in task:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate and parse due_date
        if isinstance(task['due_date'], str):
            due_date = date.fromisoformat(task['due_date'])
        else:
            due_date = task['due_date']
        
        if not isinstance(due_date, date):
            raise ValueError(f"Invalid due_date format: {task['due_date']}")
        
        # Validate estimated_hours
        estimated_hours = task['estimated_hours']
        if estimated_hours < 0:
            raise ValueError(f"estimated_hours cannot be negative: {estimated_hours}")
        
        # Validate importance
        importance = task['importance']
        if not (1 <= importance <= 10):
            raise ValueError(f"importance must be between 1 and 10: {importance}")
        
        # Calculate component scores
        urgency = self.calculate_urgency_score(due_date, today)
        importance_score = self.calculate_importance_score(importance)
        effort = self.calculate_effort_score(estimated_hours)
        dependency = self.calculate_dependency_score(task, tasks)
        
        # Check if overdue
        is_overdue = (due_date - today).days < 0
        overdue_days = abs((due_date - today).days) if is_overdue else 0
        
        # Apply overdue multiplier if applicable
        if is_overdue:
            urgency = abs(urgency) * self.weights['overdue_multiplier']
        
        # Calculate weighted final score
        final_score = (
            urgency * self.weights['urgency_weight'] +
            importance_score * self.weights['importance_weight'] +
            effort * self.weights['effort_weight'] +
            dependency * self.weights['dependency_weight']
        )
        
        # Ensure score is non-negative
        final_score = max(0, final_score)
        
        # Generate explanation
        explanation_parts = []
        
        if is_overdue:
            explanation_parts.append(f"⚠️ OVERDUE by {overdue_days} day(s) - CRITICAL PRIORITY")
        
        if urgency >= 70:
            explanation_parts.append("High urgency (due soon)")
        elif urgency >= 30:
            explanation_parts.append("Moderate urgency")
        else:
            explanation_parts.append("Low urgency (plenty of time)")
        
        if importance_score >= 70:
            explanation_parts.append("High importance")
        elif importance_score >= 40:
            explanation_parts.append("Moderate importance")
        else:
            explanation_parts.append("Low importance")
        
        if effort >= 70:
            explanation_parts.append("Quick task (low effort)")
        elif effort >= 40:
            explanation_parts.append("Moderate effort required")
        else:
            explanation_parts.append("High effort task")
        
        deps = task.get('dependencies', [])
        blocking = sum(1 for t in tasks if task.get('id') in t.get('dependencies', []))
        if blocking > 0:
            explanation_parts.append(f"Blocks {blocking} other task(s)")
        if deps:
            explanation_parts.append(f"Depends on {len(deps)} task(s)")
        
        explanation = ". ".join(explanation_parts) + "."
        
        return {
            'score': round(final_score, 2),
            'breakdown': {
                'urgency': round(urgency, 2),
                'importance': round(importance_score, 2),
                'effort': round(effort, 2),
                'dependency': round(dependency, 2),
            },
            'explanation': explanation,
            'is_overdue': is_overdue,
            'overdue_days': overdue_days,
        }

    def analyze_tasks(self, tasks: List[Dict[str, Any]], profile: str = None) -> Dict[str, Any]:
        """
        Analyze and score a list of tasks.
        Returns sorted tasks with scores and explanations.
        """
        if profile and profile != self.profile:
            self.profile = profile
            self.weights = self.PROFILES[profile]
        
        if not tasks:
            return {
                'tasks': [],
                'profile': self.profile,
                'errors': []
            }
        
        # Validate all tasks have IDs
        for i, task in enumerate(tasks):
            if 'id' not in task:
                task['id'] = i + 1
        
        # Check for circular dependencies
        cycle = self.detect_circular_dependencies(tasks)
        if cycle:
            return {
                'tasks': [],
                'profile': self.profile,
                'errors': [f"Circular dependency detected involving tasks: {cycle}"]
            }
        
        # Validate dependencies exist
        task_ids = {task['id'] for task in tasks}
        errors = []
        for task in tasks:
            deps = task.get('dependencies', [])
            invalid_deps = [dep for dep in deps if dep not in task_ids]
            if invalid_deps:
                errors.append(f"Task '{task.get('title', task['id'])}' has invalid dependencies: {invalid_deps}")
        
        if errors:
            return {
                'tasks': [],
                'profile': self.profile,
                'errors': errors
            }
        
        # Score all tasks
        today = date.today()
        scored_tasks = []
        
        for task in tasks:
            try:
                result = self.score_task(task, tasks, today)
                scored_tasks.append({
                    **task,
                    **result
                })
            except Exception as e:
                errors.append(f"Error scoring task '{task.get('title', task['id'])}': {str(e)}")
        
        # Sort by score (highest first)
        scored_tasks.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'tasks': scored_tasks,
            'profile': self.profile,
            'errors': errors
        }




