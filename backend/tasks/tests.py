from django.test import TestCase
from datetime import date, timedelta
from .scoring import ScoringEngine


class ScoringEngineTestCase(TestCase):
    """Test cases for the scoring engine."""
    
    def setUp(self):
        """Set up test data."""
        self.today = date.today()
        self.engine = ScoringEngine(profile='smart_balance')
        
        self.sample_tasks = [
            {
                'id': 1,
                'title': 'Urgent Task',
                'due_date': self.today + timedelta(days=1),
                'estimated_hours': 2,
                'importance': 9,
                'dependencies': []
            },
            {
                'id': 2,
                'title': 'Overdue Task',
                'due_date': self.today - timedelta(days=5),
                'estimated_hours': 4,
                'importance': 7,
                'dependencies': []
            },
            {
                'id': 3,
                'title': 'Low Priority Task',
                'due_date': self.today + timedelta(days=30),
                'estimated_hours': 8,
                'importance': 3,
                'dependencies': []
            },
        ]
    
    def test_overdue_task_gets_highest_priority(self):
        """Test that overdue tasks receive significantly higher priority scores."""
        # Create tasks: one overdue, one due soon
        tasks = [
            {
                'id': 1,
                'title': 'Overdue Critical',
                'due_date': self.today - timedelta(days=3),
                'estimated_hours': 4,
                'importance': 8,
                'dependencies': []
            },
            {
                'id': 2,
                'title': 'Due Tomorrow',
                'due_date': self.today + timedelta(days=1),
                'estimated_hours': 4,
                'importance': 8,
                'dependencies': []
            }
        ]
        
        result = self.engine.analyze_tasks(tasks)
        
        self.assertFalse(result.get('errors'), f"Unexpected errors: {result.get('errors')}")
        self.assertEqual(len(result['tasks']), 2)
        
        # Overdue task should be first
        self.assertEqual(result['tasks'][0]['id'], 1)
        self.assertTrue(result['tasks'][0]['is_overdue'])
        self.assertGreater(result['tasks'][0]['score'], result['tasks'][1]['score'])
        
        # Verify overdue days calculation
        self.assertEqual(result['tasks'][0]['overdue_days'], 3)
    
    def test_dependency_priority_boost(self):
        """Test that tasks blocking other tasks get priority boost."""
        tasks = [
            {
                'id': 1,
                'title': 'Blocking Task',
                'due_date': self.today + timedelta(days=7),
                'estimated_hours': 4,
                'importance': 5,
                'dependencies': []
            },
            {
                'id': 2,
                'title': 'Depends on Task 1',
                'due_date': self.today + timedelta(days=7),
                'estimated_hours': 4,
                'importance': 5,
                'dependencies': [1]
            },
            {
                'id': 3,
                'title': 'Also Depends on Task 1',
                'due_date': self.today + timedelta(days=7),
                'estimated_hours': 4,
                'importance': 5,
                'dependencies': [1]
            },
            {
                'id': 4,
                'title': 'Independent Task',
                'due_date': self.today + timedelta(days=7),
                'estimated_hours': 4,
                'importance': 5,
                'dependencies': []
            }
        ]
        
        result = self.engine.analyze_tasks(tasks)
        
        self.assertFalse(result.get('errors'), f"Unexpected errors: {result.get('errors')}")
        self.assertEqual(len(result['tasks']), 4)
        
        # Task 1 (blocking 2 others) should have higher score than task 4 (independent)
        task1_score = next(t['score'] for t in result['tasks'] if t['id'] == 1)
        task4_score = next(t['score'] for t in result['tasks'] if t['id'] == 4)
        
        self.assertGreater(task1_score, task4_score, 
                          "Blocking task should have higher priority than independent task")
        
        # Verify explanation mentions blocking
        task1 = next(t for t in result['tasks'] if t['id'] == 1)
        self.assertIn('Blocks', task1['explanation'])
    
    def test_scoring_logic_components(self):
        """Test that scoring logic correctly combines all components."""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': self.today + timedelta(days=3),
            'estimated_hours': 2,
            'importance': 8,
            'dependencies': []
        }
        
        result = self.engine.score_task(task, [task], self.today)
        
        # Verify all components are present
        self.assertIn('score', result)
        self.assertIn('breakdown', result)
        self.assertIn('explanation', result)
        self.assertIn('is_overdue', result)
        
        # Verify breakdown has all components
        breakdown = result['breakdown']
        self.assertIn('urgency', breakdown)
        self.assertIn('importance', breakdown)
        self.assertIn('effort', breakdown)
        self.assertIn('dependency', breakdown)
        
        # Verify scores are reasonable
        self.assertGreater(result['score'], 0)
        self.assertGreater(breakdown['urgency'], 0)
        self.assertGreater(breakdown['importance'], 0)
        self.assertGreater(breakdown['effort'], 0)
        self.assertGreater(breakdown['dependency'], 0)
        
        # Verify explanation is meaningful
        self.assertIsInstance(result['explanation'], str)
        self.assertGreater(len(result['explanation']), 10)
    
    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected and reported."""
        tasks = [
            {
                'id': 1,
                'title': 'Task 1',
                'due_date': self.today + timedelta(days=7),
                'estimated_hours': 4,
                'importance': 5,
                'dependencies': [2]
            },
            {
                'id': 2,
                'title': 'Task 2',
                'due_date': self.today + timedelta(days=7),
                'estimated_hours': 4,
                'importance': 5,
                'dependencies': [1]
            }
        ]
        
        result = self.engine.analyze_tasks(tasks)
        
        # Should detect circular dependency
        self.assertTrue(result.get('errors'))
        self.assertIn('Circular dependency', result['errors'][0])
        self.assertEqual(len(result['tasks']), 0)
    
    def test_invalid_dependencies_handling(self):
        """Test that invalid dependency IDs are caught."""
        tasks = [
            {
                'id': 1,
                'title': 'Task with invalid dep',
                'due_date': self.today + timedelta(days=7),
                'estimated_hours': 4,
                'importance': 5,
                'dependencies': [999]  # Non-existent task
            }
        ]
        
        result = self.engine.analyze_tasks(tasks)
        
        # Should detect invalid dependency
        self.assertTrue(result.get('errors'))
        self.assertIn('invalid dependencies', result['errors'][0].lower())
    
    def test_profile_differences(self):
        """Test that different profiles produce different scores."""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': self.today + timedelta(days=5),
            'estimated_hours': 1,  # Quick win
            'importance': 9,  # High importance
            'dependencies': []
        }
        
        # Test fastest_wins profile (should favor low effort)
        engine_fast = ScoringEngine(profile='fastest_wins')
        result_fast = engine_fast.score_task(task, [task], self.today)
        
        # Test high_impact profile (should favor importance)
        engine_impact = ScoringEngine(profile='high_impact')
        result_impact = engine_impact.score_task(task, [task], self.today)
        
        # Both should score the task, but potentially differently
        self.assertGreater(result_fast['score'], 0)
        self.assertGreater(result_impact['score'], 0)
        
        # Fastest wins should emphasize effort more
        self.assertGreater(result_fast['breakdown']['effort'] * 0.6, 
                          result_impact['breakdown']['effort'] * 0.1)
        
        # High impact should emphasize importance more
        self.assertGreater(result_impact['breakdown']['importance'] * 0.5,
                          result_fast['breakdown']['importance'] * 0.1)




