# Smart Task Analyzer

A production-quality Django-based task prioritization system with an intelligent scoring algorithm and modern web interface.

## Project Overview

The Smart Task Analyzer is a full-stack web application that helps users prioritize tasks using a sophisticated multi-factor scoring algorithm. The system analyzes tasks based on urgency, importance, estimated effort, and dependencies to provide optimal task ordering recommendations.

### Key Features

- **Multi-Profile Scoring**: Four different prioritization profiles (Smart Balance, Fastest Wins, High Impact, Deadline Driven)
- **Dependency Management**: Detects circular dependencies and prioritizes blocking tasks
- **Overdue Detection**: Automatically boosts priority for overdue tasks
- **RESTful API**: Clean Django REST Framework endpoints
- **Modern UI**: Responsive, color-coded interface with visual score breakdowns
- **Comprehensive Validation**: Handles all edge cases with proper error messages

## Installation Steps

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run database migrations:
```bash
python manage.py migrate
```

6. (Optional) Create a superuser for admin access:
```bash
python manage.py createsuperuser
```

### Frontend Setup

The frontend is static HTML/CSS/JS and requires no build process. Simply open `frontend/index.html` in a web browser, or serve it using a local web server.

## How to Run Backend

1. Navigate to the backend directory:
```bash
cd backend
```

2. Activate your virtual environment (if not already active)

3. Start the Django development server:
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### API Endpoints

- `POST /api/tasks/analyze/` - Analyze and score a list of tasks
- `GET /api/tasks/suggest/` - Get top 3 task suggestions from database

## How to Run Frontend

### Option 1: Direct File Access
Simply open `frontend/index.html` in your web browser. Note: You may need to configure CORS if accessing from `file://` protocol.

### Option 2: Using Python HTTP Server
```bash
cd frontend
python -m http.server 8080
```
Then navigate to `http://localhost:8080` in your browser.

### Option 3: Using Node.js http-server
```bash
npx http-server frontend -p 8080
```

**Important**: Update the `API_BASE_URL` in `frontend/index.html` (line 8) if your backend is running on a different port or host.

## Deployment

This project can be deployed to:
- **Frontend**: Vercel (recommended)
- **Backend**: Render (recommended)

### Quick Deploy

See **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** for a 10-minute deployment guide.

### Detailed Deployment Instructions

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for comprehensive deployment instructions including:
- Step-by-step setup for Vercel and Render
- Environment variable configuration
- CORS setup
- Troubleshooting guide

### Deployment Checklist

1. ✅ Backend deployed to Render
2. ✅ Frontend deployed to Vercel
3. ✅ API URL updated in `frontend/index.html`
4. ✅ CORS configured on backend
5. ✅ Environment variables set correctly

## Algorithm Explanation

The Smart Task Analyzer uses a weighted scoring algorithm that combines multiple factors to determine task priority. The algorithm is designed to be flexible and configurable through different "profiles" that emphasize different aspects of task management.

### Core Components

1. **Urgency Score (0-100)**: Based on days until due date
   - Overdue tasks receive exponentially higher scores
   - Tasks due today or tomorrow get maximum urgency
   - Urgency decreases logarithmically as the due date moves further out
   - Formula accounts for overdue penalty multiplier

2. **Importance Score (0-100)**: Normalized from user-provided importance (1-10)
   - Direct linear mapping: importance 10 = 100 points, importance 1 = 10 points
   - This ensures high-importance tasks are always considered

3. **Effort Score (0-100)**: Inverse relationship with estimated hours
   - Lower effort tasks score higher (encouraging quick wins)
   - Tasks under 1 hour get maximum score
   - Score decreases as effort increases, with diminishing returns

4. **Dependency Score (0-100)**: Complex calculation based on blocking relationships
   - Tasks that block many other tasks get priority boost
   - Tasks with fewer dependencies get slight boost (can start sooner)
   - Weighted combination: 60% blocking score, 40% dependency count score

### Scoring Formula

```
Final Score = (Urgency × Urgency_Weight) + 
              (Importance × Importance_Weight) + 
              (Effort × Effort_Weight) + 
              (Dependency × Dependency_Weight)
```

If a task is overdue, the urgency component is multiplied by the `overdue_multiplier` (typically 2.0-3.0 depending on profile).

### Profile Differences

- **Smart Balance**: Balanced weights (35% urgency, 30% importance, 20% effort, 15% dependency)
- **Fastest Wins**: Emphasizes low effort (60% effort weight) to maximize task completion
- **High Impact**: Prioritizes importance (50% importance weight) for maximum value
- **Deadline Driven**: Focuses on urgency (60% urgency weight) with high overdue multiplier (3.0)

### Edge Case Handling

- **Circular Dependencies**: Detected using DFS algorithm, returns error before scoring
- **Invalid Dependencies**: Validated against task list, returns descriptive error
- **Missing Fields**: All required fields validated with clear error messages
- **Invalid Dates**: Date format validation with helpful error messages
- **Negative Effort**: Rejected with validation error
- **Invalid Importance Range**: Must be 1-10, validated before processing

## Design Decisions

### Backend Architecture

1. **Django REST Framework**: Chosen for rapid API development and built-in serialization
2. **Separate Scoring Module**: `scoring.py` is isolated for easy testing and algorithm refinement
3. **JSONField for Dependencies**: Flexible storage without additional join tables
4. **Profile-Based Configuration**: Easy to add new profiles without code changes
5. **Comprehensive Error Handling**: All edge cases return structured error responses

### Frontend Architecture

1. **Vanilla JavaScript**: No framework dependencies for simplicity and performance
2. **Tab-Based Input**: Supports both single task entry and bulk JSON import
3. **Visual Score Breakdown**: Bar charts show component contributions for transparency
4. **Color-Coded Priority**: Red (high), Orange (medium), Green (low) for quick visual scanning
5. **Responsive Design**: Works on desktop, tablet, and mobile devices

### Algorithm Design

1. **Weighted Sum Approach**: Simple, interpretable, and easily adjustable
2. **Normalized Components**: All scores on 0-100 scale for consistent weighting
3. **Overdue Multiplier**: Separate handling prevents overdue tasks from dominating normal scoring
4. **Dependency Detection**: DFS-based cycle detection is efficient and accurate
5. **Blocking Priority**: Tasks that block others get boost, encouraging dependency resolution

## Time Spent for Each Section

- **Project Setup & Configuration**: 30 minutes
  - Django project structure, settings, URLs, CORS configuration

- **Data Models**: 20 minutes
  - Task model design, field validation, admin interface

- **Scoring Algorithm**: 2 hours
  - Core algorithm design, profile system, component calculations, edge case handling

- **API Development**: 1.5 hours
  - Serializers, views, error handling, input validation

- **Frontend Development**: 2 hours
  - HTML structure, CSS styling, JavaScript functionality, API integration

- **Testing**: 1 hour
  - Unit tests for scoring logic, edge cases, dependency handling

- **Documentation**: 45 minutes
  - README, code comments, algorithm explanation

**Total Estimated Time**: ~8 hours

## Trade-offs

### Algorithm Complexity vs. Interpretability

**Decision**: Chose weighted sum over machine learning
- **Pros**: Easy to understand, explainable, adjustable weights
- **Cons**: May not capture complex non-linear relationships

### Framework vs. Vanilla JS

**Decision**: Vanilla JavaScript for frontend
- **Pros**: No build process, fast load times, easy to understand
- **Cons**: More manual DOM manipulation, no component reusability

### Database vs. In-Memory Processing

**Decision**: In-memory scoring with optional database storage
- **Pros**: Fast analysis, no database dependency for core functionality
- **Cons**: Cannot persist analysis history without additional work

### Real-time vs. Request-Response

**Decision**: Synchronous request-response API
- **Pros**: Simple implementation, predictable behavior
- **Cons**: Large task lists may cause timeout (mitigated by client-side validation)

## Edge-Case Handling Explanation

### Circular Dependencies

**Problem**: Task A depends on B, B depends on A creates infinite loop
**Solution**: DFS-based cycle detection before scoring
**Implementation**: `detect_circular_dependencies()` uses recursion stack to identify cycles
**Error Response**: Clear message listing all tasks in the cycle

### Invalid Dependencies

**Problem**: Task references dependency ID that doesn't exist
**Solution**: Validate all dependency IDs against task list
**Implementation**: Check each task's dependencies against available task IDs
**Error Response**: Lists all invalid dependencies with task context

### Missing Required Fields

**Problem**: Task missing title, due_date, estimated_hours, or importance
**Solution**: Multi-level validation (client-side and server-side)
**Implementation**: Serializer validation + manual field checks in views
**Error Response**: Specific field names and task index

### Invalid Date Formats

**Problem**: Date string in wrong format or unparseable
**Solution**: Try-catch with `date.fromisoformat()` and validation
**Implementation**: Check format before parsing, provide helpful error
**Error Response**: Shows expected format (YYYY-MM-DD) and received value

### Negative or Invalid Numbers

**Problem**: Negative hours, importance outside 1-10 range
**Solution**: Django validators + manual checks
**Implementation**: `MinValueValidator`, `MaxValueValidator` on model + view checks
**Error Response**: Clear range requirements and received value

### Empty Task Lists

**Problem**: User submits empty array or no tasks
**Solution**: Early return with empty result
**Implementation**: Check length before processing
**Response**: Returns empty tasks array with no errors

## Future Improvement Plan

### Short-term (1-2 weeks)

1. **User Authentication**: Add user accounts to save and manage task lists
2. **Task Persistence**: Save analyzed tasks to database with timestamps
3. **Export Functionality**: Export prioritized list as CSV, JSON, or calendar file
4. **History View**: Show previous analyses and compare results

### Medium-term (1-2 months)

1. **Machine Learning Integration**: Train model on user feedback to improve scoring
2. **Collaborative Features**: Share task lists with team members
3. **Calendar Integration**: Sync with Google Calendar, Outlook, etc.
4. **Time Tracking**: Track actual vs. estimated hours for better predictions
5. **Recurring Tasks**: Support for repeating tasks with smart scheduling

### Long-term (3-6 months)

1. **Mobile App**: Native iOS/Android apps with offline support
2. **AI Suggestions**: Generate task breakdowns and subtasks automatically
3. **Integration Hub**: Connect with project management tools (Jira, Trello, Asana)
4. **Analytics Dashboard**: Visualize productivity patterns and bottlenecks
5. **Multi-Objective Optimization**: Support for multiple simultaneous goals

### Algorithm Enhancements

1. **Context Awareness**: Consider time of day, energy levels, calendar availability
2. **Learning from History**: Adjust weights based on what users actually complete
3. **Team Coordination**: Factor in team member availability and skills
4. **Resource Constraints**: Consider budget, equipment, or other resource limits
5. **Risk Assessment**: Factor in task failure probability and impact

## License

This project is provided as-is for educational and commercial use.

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.

---

**Built with Django, Django REST Framework, and Vanilla JavaScript**



