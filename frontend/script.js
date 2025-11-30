// Task Analyzer Frontend JavaScript

// API Base URL - Set by script tag in index.html or fallback to Render backend
const API_BASE_URL = (typeof window !== 'undefined' && window.API_BASE_URL) 
    ? window.API_BASE_URL 
    : 'https://task-analyzer-backend-gx1y.onrender.com/api';

// State management
let tasks = [];
let currentTab = 'single';

// DOM Elements
const singleTaskForm = document.getElementById('single-task-form');
const bulkJsonForm = document.getElementById('bulk-json-form');
const tabButtons = document.querySelectorAll('.tab-button');
const taskForm = document.getElementById('task-form');
const addTaskBtn = document.getElementById('add-task-btn');
const analyzeBtn = document.getElementById('analyze-btn');
const jsonInput = document.getElementById('json-input');
const tasksContainer = document.getElementById('tasks-container');
const taskCount = document.getElementById('task-count');
const resultsSection = document.getElementById('results-section');
const resultsContainer = document.getElementById('results-container');
const errorMessage = document.getElementById('error-message');
const profileSelect = document.getElementById('profile');
const profileDescription = document.getElementById('profile-description');

// Profile descriptions
const profileDescriptions = {
    'smart_balance': 'Balanced approach considering urgency, importance, effort, and dependencies.',
    'fastest_wins': 'Prioritizes quick tasks with low effort to maximize completed tasks.',
    'high_impact': 'Focuses on high-importance tasks regardless of effort required.',
    'deadline_driven': 'Emphasizes tasks with approaching deadlines and overdue items.'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateTaskCount();
    updateProfileDescription();
});

function setupEventListeners() {
    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tab = button.dataset.tab;
            switchTab(tab);
        });
    });

    // Form submission
    addTaskBtn.addEventListener('click', handleAddTask);
    analyzeBtn.addEventListener('click', handleAnalyze);
    
    // Profile change
    profileSelect.addEventListener('change', updateProfileDescription);
}

function switchTab(tab) {
    currentTab = tab;
    
    // Update tab buttons
    tabButtons.forEach(btn => {
        if (btn.dataset.tab === tab) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update tab content
    if (tab === 'single') {
        singleTaskForm.classList.add('active');
        bulkJsonForm.classList.remove('active');
    } else {
        singleTaskForm.classList.remove('active');
        bulkJsonForm.classList.add('active');
    }
}

function updateProfileDescription() {
    const profile = profileSelect.value;
    profileDescription.textContent = profileDescriptions[profile] || '';
}

function handleAddTask(e) {
    e.preventDefault();
    
    if (!taskForm.checkValidity()) {
        taskForm.reportValidity();
        return;
    }
    
    const formData = new FormData(taskForm);
    const task = {
        id: tasks.length + 1,
        title: formData.get('title'),
        due_date: formData.get('due_date'),
        estimated_hours: parseInt(formData.get('estimated_hours')),
        importance: parseInt(formData.get('importance')),
        dependencies: parseDependencies(formData.get('dependencies'))
    };
    
    // Validate
    if (!validateTask(task)) {
        return;
    }
    
    tasks.push(task);
    taskForm.reset();
    renderTaskList();
    updateTaskCount();
}

function parseDependencies(depsString) {
    if (!depsString || !depsString.trim()) {
        return [];
    }
    return depsString.split(',')
        .map(d => parseInt(d.trim()))
        .filter(d => !isNaN(d));
}

function validateTask(task) {
    if (!task.title || !task.title.trim()) {
        showError('Task title is required');
        return false;
    }
    
    if (!task.due_date) {
        showError('Due date is required');
        return false;
    }
    
    if (isNaN(task.estimated_hours) || task.estimated_hours < 0) {
        showError('Estimated hours must be a non-negative number');
        return false;
    }
    
    if (isNaN(task.importance) || task.importance < 1 || task.importance > 10) {
        showError('Importance must be between 1 and 10');
        return false;
    }
    
    return true;
}

function renderTaskList() {
    tasksContainer.innerHTML = '';
    
    if (tasks.length === 0) {
        tasksContainer.innerHTML = '<p style="color: var(--text-secondary);">No tasks added yet.</p>';
        return;
    }
    
    tasks.forEach((task, index) => {
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item';
        taskItem.innerHTML = `
            <div class="task-item-info">
                <div class="task-item-title">${escapeHtml(task.title)}</div>
                <div class="task-item-details">
                    Due: ${task.due_date} | Hours: ${task.estimated_hours} | Importance: ${task.importance}
                    ${task.dependencies.length > 0 ? ` | Deps: ${task.dependencies.join(', ')}` : ''}
                </div>
            </div>
            <button class="task-item-remove" onclick="removeTask(${index})">Remove</button>
        `;
        tasksContainer.appendChild(taskItem);
    });
}

function removeTask(index) {
    tasks.splice(index, 1);
    // Reassign IDs
    tasks.forEach((task, i) => {
        task.id = i + 1;
    });
    renderTaskList();
    updateTaskCount();
}

function updateTaskCount() {
    taskCount.textContent = tasks.length;
}

function handleAnalyze() {
    hideError();
    
    let tasksToAnalyze = [];
    
    if (currentTab === 'single') {
        if (tasks.length === 0) {
            showError('Please add at least one task before analyzing.');
            return;
        }
        tasksToAnalyze = tasks;
    } else {
        // Bulk JSON mode
        const jsonText = jsonInput.value.trim();
        if (!jsonText) {
            showError('Please paste JSON tasks in the textarea.');
            return;
        }
        
        try {
            tasksToAnalyze = JSON.parse(jsonText);
            if (!Array.isArray(tasksToAnalyze)) {
                throw new Error('JSON must be an array of tasks');
            }
            
            // Validate each task
            for (let i = 0; i < tasksToAnalyze.length; i++) {
                const task = tasksToAnalyze[i];
                if (!task.id) task.id = i + 1;
                if (!validateTask(task)) {
                    throw new Error(`Task at index ${i} is invalid`);
                }
            }
        } catch (error) {
            showError(`Invalid JSON: ${error.message}`);
            return;
        }
    }
    
    // Ensure all tasks have IDs
    tasksToAnalyze.forEach((task, i) => {
        if (!task.id) task.id = i + 1;
    });
    
    analyzeTasks(tasksToAnalyze);
}

function validateDependencies(tasksToAnalyze) {
    const taskIds = new Set(tasksToAnalyze.map(t => t.id));
    const errors = [];
    
    for (const task of tasksToAnalyze) {
        const deps = task.dependencies || [];
        const invalidDeps = deps.filter(dep => !taskIds.has(dep));
        
        if (invalidDeps.length > 0) {
            errors.push(`Task "${task.title}" has invalid dependencies: ${invalidDeps.join(', ')}. These task IDs don't exist in your task list.`);
        }
        
        // Check for self-dependency
        if (deps.includes(task.id)) {
            errors.push(`Task "${task.title}" cannot depend on itself.`);
        }
    }
    
    return errors;
}

async function analyzeTasks(tasksToAnalyze) {
    const profile = profileSelect.value;
    
    // Validate dependencies before sending
    const validationErrors = validateDependencies(tasksToAnalyze);
    if (validationErrors.length > 0) {
        showError(validationErrors.join(' '));
        resultsSection.style.display = 'block';
        resultsContainer.innerHTML = '';
        return;
    }
    
    // Show loading
    resultsSection.style.display = 'block';
    resultsContainer.innerHTML = '<div class="loading">Analyzing tasks</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasksToAnalyze,
                profile: profile
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            // Handle error response - details might be a list or string
            let errorMsg = data.error || 'Analysis failed';
            if (data.details) {
                if (Array.isArray(data.details)) {
                    errorMsg += ': ' + data.details.join('; ');
                } else if (typeof data.details === 'object') {
                    errorMsg += ': ' + JSON.stringify(data.details);
                } else {
                    errorMsg += ': ' + data.details;
                }
            }
            throw new Error(errorMsg);
        }
        
        if (data.errors && data.errors.length > 0) {
            showError(data.errors.join('; '));
            return;
        }
        
        renderResults(data.tasks, data.profile);
        
    } catch (error) {
        console.error('Error:', error);
        showError(`Failed to analyze tasks: ${error.message}`);
        resultsContainer.innerHTML = '';
    }
}

function renderResults(scoredTasks, profile) {
    resultsContainer.innerHTML = '';
    
    if (scoredTasks.length === 0) {
        resultsContainer.innerHTML = '<p>No tasks to display.</p>';
        return;
    }
    
    scoredTasks.forEach((task, index) => {
        const card = createTaskCard(task, index + 1);
        resultsContainer.appendChild(card);
    });
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function createTaskCard(task, rank) {
    const card = document.createElement('div');
    
    // Determine priority class
    let priorityClass = 'priority-low';
    if (task.score >= 70) {
        priorityClass = 'priority-high';
    } else if (task.score >= 40) {
        priorityClass = 'priority-medium';
    }
    
    // Format due date
    const dueDate = new Date(task.due_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const daysUntil = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
    let dueDateText = task.due_date;
    if (daysUntil < 0) {
        dueDateText += ` (${Math.abs(daysUntil)} days overdue)`;
    } else if (daysUntil === 0) {
        dueDateText += ' (Today)';
    } else if (daysUntil === 1) {
        dueDateText += ' (Tomorrow)';
    } else {
        dueDateText += ` (${daysUntil} days)`;
    }
    
    card.className = `task-card ${priorityClass}`;
    card.innerHTML = `
        <div class="task-card-header">
            <div class="task-card-title">
                #${rank} ${escapeHtml(task.title)}
                ${task.is_overdue ? '<span class="overdue-badge">OVERDUE</span>' : ''}
            </div>
            <div class="task-card-score">Score: ${task.score.toFixed(1)}</div>
        </div>
        
        <div class="task-card-meta">
            <div class="meta-item">
                <span class="meta-label">Due Date</span>
                <span class="meta-value">${dueDateText}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Estimated Hours</span>
                <span class="meta-value">${task.estimated_hours}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Importance</span>
                <span class="meta-value">${task.importance}/10</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Dependencies</span>
                <span class="meta-value">${task.dependencies.length > 0 ? task.dependencies.join(', ') : 'None'}</span>
            </div>
        </div>
        
        <div class="task-card-explanation">
            <strong>Analysis:</strong> ${escapeHtml(task.explanation)}
        </div>
        
        <div class="task-card-breakdown">
            <div class="breakdown-title">Score Breakdown</div>
            <div class="breakdown-bars">
                <div class="breakdown-item">
                    <div class="breakdown-label">Urgency</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: ${Math.min(100, task.breakdown.urgency)}%"></div>
                    </div>
                    <div class="breakdown-value">${task.breakdown.urgency.toFixed(1)}</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Importance</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: ${Math.min(100, task.breakdown.importance)}%"></div>
                    </div>
                    <div class="breakdown-value">${task.breakdown.importance.toFixed(1)}</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Effort</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: ${Math.min(100, task.breakdown.effort)}%"></div>
                    </div>
                    <div class="breakdown-value">${task.breakdown.effort.toFixed(1)}</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Dependency</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: ${Math.min(100, task.breakdown.dependency)}%"></div>
                    </div>
                    <div class="breakdown-value">${task.breakdown.dependency.toFixed(1)}</div>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    errorMessage.style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make removeTask available globally
window.removeTask = removeTask;



