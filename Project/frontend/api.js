// API Base URL
const API_BASE = 'http://localhost:5001/api';

// API Helper Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include'
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (response.status === 401) {
            // Unauthorized - redirect to login
            window.location.href = 'index.html';
            return null;
        }

        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API error');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth API Functions
async function signup(username, password, email = null) {
    return apiCall('/auth/signup', 'POST', {
        username,
        password,
        email
    });
}

async function login(username, password) {
    return apiCall('/auth/login', 'POST', {
        username,
        password
    });
}

async function logout() {
    return apiCall('/auth/logout', 'POST');
}

async function getCurrentUser() {
    return apiCall('/auth/me', 'GET');
}

// Project API Functions
async function createProject(name, description = null) {
    return apiCall('/projects', 'POST', {
        name,
        description
    });
}

async function getProjects() {
    return apiCall('/projects', 'GET');
}

async function getProjectDetails(projectId) {
    return apiCall(`/projects/${projectId}`, 'GET');
}

async function updateProject(projectId, name = null, description = null) {
    return apiCall(`/projects/${projectId}`, 'PUT', {
        name,
        description
    });
}

async function deleteProject(projectId) {
    return apiCall(`/projects/${projectId}`, 'DELETE');
}

// Project Members API Functions
async function getProjectMembers(projectId) {
    return apiCall(`/projects/${projectId}/members`, 'GET');
}

async function addProjectMember(projectId, username, role = 'Member') {
    return apiCall(`/projects/${projectId}/members`, 'POST', {
        username,
        role
    });
}

async function removeProjectMember(projectId, memberId) {
    return apiCall(`/projects/${projectId}/members/${memberId}`, 'DELETE');
}

// Task API Functions
async function createTask(projectId, title, description = null, assignedTo = null, priority = 'Medium', dueDate = null, status = 'Pending') {
    return apiCall(`/projects/${projectId}/tasks`, 'POST', {
        title,
        description,
        assigned_to: assignedTo,
        priority,
        due_date: dueDate,
        status
    });
}

async function getProjectTasks(projectId) {
    return apiCall(`/projects/${projectId}/tasks`, 'GET');
}

async function getTaskDetails(taskId) {
    return apiCall(`/tasks/${taskId}`, 'GET');
}

async function updateTask(taskId, updates) {
    return apiCall(`/tasks/${taskId}`, 'PUT', updates);
}

async function deleteTask(taskId) {
    return apiCall(`/tasks/${taskId}`, 'DELETE');
}

async function getUserTasks(status = null) {
    let endpoint = '/dashboard/tasks';
    if (status) {
        endpoint += `?status=${status}`;
    }
    return apiCall(endpoint, 'GET');
}

// Dashboard API Functions
async function getDashboardStats() {
    return apiCall('/dashboard/stats', 'GET');
}

// Health check
async function healthCheck() {
    return apiCall('/health', 'GET');
}
