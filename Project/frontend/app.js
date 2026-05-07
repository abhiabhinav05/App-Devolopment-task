// Dashboard App Logic

let currentUser = null;
let currentProject = null;
let currentProjectId = null;
let currentProjectRole = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await initApp();
});

async function initApp() {
    try {
        const user = await getCurrentUser();
        currentUser = user;
        
        // Update UI with user info
        document.getElementById('currentUsername').textContent = user.username;
        document.getElementById('currentRole').textContent = user.role;
        document.getElementById('userAvatar').textContent = user.username.charAt(0).toUpperCase();
        
        // Load dashboard
        await loadDashboard();
        
        // Setup form handlers
        setupFormHandlers();
    } catch (error) {
        console.error('Failed to initialize app:', error);
        window.location.href = 'index.html';
    }
}

function setupFormHandlers() {
    document.getElementById('projectForm').addEventListener('submit', handleProjectSubmit);
    document.getElementById('taskForm').addEventListener('submit', handleTaskSubmit);
    document.getElementById('memberForm').addEventListener('submit', handleMemberSubmit);
}

// ===== SECTION NAVIGATION =====
function showSection(sectionId, event) {
    if (event) event.preventDefault();

    // Hide all sections
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Update nav
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const target = event ? event.target : null;
    if (target) {
        const navItem = target.closest('.nav-item');
        if (navItem) navItem.classList.add('active');
    }
    
    // Update header
    const titles = {
        'dashboard': 'Dashboard',
        'projects': 'Projects',
        'tasks': 'My Tasks'
    };
    document.getElementById('sectionTitle').textContent = titles[sectionId];
    
    // Load section data
    if (sectionId === 'projects') {
        loadProjects();
        document.getElementById('addBtn').style.display = 'inline-flex';
    } else if (sectionId === 'tasks') {
        loadUserTasks();
        document.getElementById('addBtn').style.display = 'none';
    } else {
        document.getElementById('addBtn').style.display = 'none';
    }
    
    // Close mobile menu
    document.querySelector('.sidebar').classList.remove('active');
}

function toggleMobileMenu() {
    document.querySelector('.sidebar').classList.toggle('active');
}

// ===== DASHBOARD =====
async function loadDashboard() {
    try {
        const data = await getDashboardStats();
        
        // Update stats
        document.getElementById('totalTasks').textContent = data.stats.total_tasks || 0;
        document.getElementById('pendingTasks').textContent = data.stats.pending_tasks || 0;
        document.getElementById('inProgressTasks').textContent = data.stats.in_progress_tasks || 0;
        document.getElementById('completedTasks').textContent = data.stats.completed_tasks || 0;
        document.getElementById('overdueTasks').textContent = data.stats.overdue_tasks || 0;
        
        // Load recent tasks
        loadRecentTasks(data.recent_tasks);
        
        // Load projects overview
        loadProjectsOverview(data.projects);
    } catch (error) {
        showMessage('Failed to load dashboard', 'error');
    }
}

function loadRecentTasks(tasks) {
    const container = document.getElementById('recentTasksList');
    
    if (tasks.length === 0) {
        container.innerHTML = '<p class="empty-state">No tasks assigned yet</p>';
        return;
    }
    
    container.innerHTML = tasks.slice(0, 5).map(task => `
        <div class="task-card ${task.priority.toLowerCase()}-priority">
            <div class="task-content">
                <div class="task-title" onclick="openTaskDetail(${task.id})">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    <span class="task-status ${task.status.toLowerCase()}">${task.status}</span>
                    ${task.due_date ? `<span>Due: ${formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

async function openTaskDetail(taskId) {
    try {
        const data = await getTaskDetails(taskId);
        const task = data.task;
        const message = `Task: ${task.title}\nStatus: ${task.status}\nPriority: ${task.priority}\nDue: ${task.due_date || 'None'}\nAssigned to: ${task.assigned_to_name || 'Unassigned'}\nDescription: ${task.description || 'No description'}`;
        alert(message);
    } catch (error) {
        showMessage('Failed to load task details', 'error');
    }
}

function loadProjectsOverview(projects) {
    const container = document.getElementById('projectsOverview');
    
    if (projects.length === 0) {
        container.innerHTML = '<p class="empty-state">No projects yet. <a href="#" onclick="showSection(\'projects\')">Create one</a></p>';
        return;
    }
    
    container.innerHTML = projects.map(project => `
        <div class="project-card" onclick="openProjectDetail(${project.id})">
            <h3>${escapeHtml(project.name)}</h3>
            <p>${escapeHtml(project.description || 'No description')}</p>
            <div class="project-footer">
                <span>${formatDate(project.created_at)}</span>
                <span>Owner: ${escapeHtml(project.owner_id)}</span>
            </div>
        </div>
    `).join('');
}

// ===== PROJECTS =====
async function loadProjects() {
    try {
        const data = await getProjects();
        displayProjects(data.projects);
    } catch (error) {
        showMessage('Failed to load projects', 'error');
    }
}

function displayProjects(projects) {
    const container = document.getElementById('projectsList');
    
    if (projects.length === 0) {
        container.innerHTML = '<p class="empty-state">No projects yet. Create one to get started!</p>';
        return;
    }
    
    container.innerHTML = projects.map(project => `
        <div class="project-card" onclick="openProjectDetail(${project.id})">
            <h3>${escapeHtml(project.name)}</h3>
            <p>${escapeHtml(project.description || 'No description')}</p>
            <div class="project-footer">
                <span>${formatDate(project.created_at)}</span>
            </div>
        </div>
    `).join('');
}

function showProjectModal() {
    document.getElementById('projectModalTitle').textContent = 'Create Project';
    const projectForm = document.getElementById('projectForm');
    projectForm.reset();
    projectForm.dataset.projectId = '';
    openModal('projectModal');
}

async function handleProjectSubmit(e) {
    e.preventDefault();
    
    const name = document.getElementById('projectName').value;
    const description = document.getElementById('projectDescription').value;
    const projectForm = document.getElementById('projectForm');
    const projectId = projectForm.dataset.projectId;

    try {
        if (projectId) {
            await updateProject(parseInt(projectId), name, description);
            showMessage('Project updated successfully', 'success');
        } else {
            await createProject(name, description);
            showMessage('Project created successfully', 'success');
        }
        closeModal('projectModal');
        await loadProjects();
    } catch (error) {
        showMessage(error.message || 'Failed to save project', 'error');
    }
}

// ===== PROJECT DETAIL =====
async function openProjectDetail(projectId) {
    try {
        const data = await getProjectDetails(projectId);
        currentProject = data.project;
        currentProjectId = projectId;
        currentProjectRole = data.user_role;
        
        document.getElementById('detailProjectName').textContent = data.project.name;
        document.getElementById('detailProjectDescription').textContent = data.project.description || 'No description';
        
        const canManageProject = currentProject.owner_id === currentUser.id || currentProjectRole === 'Admin';
        document.getElementById('addMemberBtn').style.display = canManageProject ? 'inline-flex' : 'none';
        document.getElementById('createTaskBtn').style.display = canManageProject ? 'inline-flex' : 'none';
        document.getElementById('editProjectBtn').style.display = canManageProject ? 'inline-flex' : 'none';
        document.getElementById('deleteProjectBtn').style.display = currentProject.owner_id === currentUser.id ? 'inline-flex' : 'none';
        
        displayMembers(data.members);
        displayProjectTasks(data.tasks);
        
        openModal('projectDetailModal');
    } catch (error) {
        showMessage('Failed to load project details', 'error');
    }
}

function displayMembers(members) {
    const container = document.getElementById('membersList');
    const canManageMembers = currentProject && (currentProject.owner_id === currentUser.id || currentProjectRole === 'Admin');
    
    if (members.length === 0) {
        container.innerHTML = '<p class="empty-state">No members yet</p>';
        return;
    }
    
    container.innerHTML = members.map(member => `
        <div class="member-card">
            <div class="member-info">
                <div class="member-name">${escapeHtml(member.username)}</div>
                <div class="member-role">${member.role}</div>
            </div>
            ${canManageMembers && member.user_id !== currentProject.owner_id ? `
                <button class="btn btn-small danger" onclick="removeMember(${member.user_id})">Remove</button>
            ` : ''}
        </div>
    `).join('');
}

function displayProjectTasks(tasks) {
    const container = document.getElementById('projectTasksList');
    const canManageProject = currentProject && (currentProject.owner_id === currentUser.id || currentProjectRole === 'Admin');
    
    if (tasks.length === 0) {
        container.innerHTML = '<p class="empty-state">No tasks yet</p>';
        return;
    }
    
    container.innerHTML = tasks.map(task => {
        const canEdit = canManageProject || task.assigned_to === currentUser.id;
        const canDelete = canManageProject;
        return `
        <div class="task-card ${task.priority.toLowerCase()}-priority">
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    <span class="task-status ${task.status.toLowerCase()}">${task.status}</span>
                    ${task.assigned_to_name ? `<span>Assigned to: ${escapeHtml(task.assigned_to_name)}</span>` : ''}
                    ${task.due_date ? `<span>Due: ${formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
            <div class="task-actions">
                ${canEdit ? `<button class="btn btn-small" onclick="openEditTaskModal(${task.id})">Edit</button>` : ''}
                ${canDelete ? `<button class="btn btn-small danger" onclick="deleteTaskFromDetail(${task.id})">Delete</button>` : ''}
            </div>
        </div>
        `;
    }).join('');
}

function showEditProjectModal() {
    if (!currentProject) return;
    document.getElementById('projectModalTitle').textContent = 'Edit Project';
    const projectForm = document.getElementById('projectForm');
    projectForm.dataset.projectId = currentProject.id;
    document.getElementById('projectName').value = currentProject.name;
    document.getElementById('projectDescription').value = currentProject.description || '';
    openModal('projectModal');
}

async function deleteProject() {
    if (!currentProject) return;
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    try {
        await deleteProject(currentProject.id);
        showMessage('Project deleted successfully', 'success');
        closeModal('projectDetailModal');
        await loadProjects();
    } catch (error) {
        showMessage(error.message || 'Failed to delete project', 'error');
    }
}

// ===== MEMBERS =====
function showMemberModal() {
    if (!currentProjectId) return;
    document.getElementById('memberForm').reset();
    openModal('memberModal');
}

async function handleMemberSubmit(e) {
    e.preventDefault();
    
    const username = document.getElementById('memberUsername').value;
    const role = document.getElementById('memberRole').value;
    
    try {
        await addProjectMember(currentProjectId, username, role);
        showMessage('Member added successfully', 'success');
        closeModal('memberModal');
        const data = await getProjectDetails(currentProjectId);
        displayMembers(data.members);
    } catch (error) {
        showMessage(error.message || 'Failed to add member', 'error');
    }
}

async function removeMember(memberId) {
    if (!currentProjectId) return;
    if (!confirm('Are you sure you want to remove this member?')) return;
    
    try {
        await removeProjectMember(currentProjectId, memberId);
        showMessage('Member removed successfully', 'success');
        const data = await getProjectDetails(currentProjectId);
        displayMembers(data.members);
    } catch (error) {
        showMessage(error.message || 'Failed to remove member', 'error');
    }
}

// ===== TASKS =====
function showTaskModal() {
    if (!currentProjectId) return;
    document.getElementById('taskModalTitle').textContent = 'Create Task';
    const taskForm = document.getElementById('taskForm');
    taskForm.reset();
    taskForm.dataset.taskId = '';
    
    // Load project members for assignment
    loadTaskAssignees();
    openModal('taskModal');
}

async function loadTaskAssignees() {
    if (!currentProjectId) return;
    
    try {
        const data = await getProjectMembers(currentProjectId);
        const select = document.getElementById('taskAssignee');
        select.innerHTML = '<option value="">Unassigned</option>' + 
            data.members.map(m => `<option value="${m.user_id}">${escapeHtml(m.username)}</option>`).join('');
    } catch (error) {
        console.error('Failed to load assignees:', error);
    }
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    
    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    const priority = document.getElementById('taskPriority').value;
    const status = document.getElementById('taskStatus').value;
    const dueDate = document.getElementById('taskDueDate').value;
    const assignedTo = document.getElementById('taskAssignee').value;
    const taskForm = document.getElementById('taskForm');
    const taskId = taskForm.dataset.taskId;
    
    if (!currentProjectId) return;
    
    try {
        if (taskId) {
            await updateTask(parseInt(taskId), {
                title,
                description,
                assigned_to: assignedTo ? parseInt(assignedTo) : null,
                status,
                priority,
                due_date: dueDate
            });
            showMessage('Task updated successfully', 'success');
        } else {
            await createTask(
                currentProjectId,
                title,
                description,
                assignedTo ? parseInt(assignedTo) : null,
                priority,
                dueDate,
                status
            );
            showMessage('Task created successfully', 'success');
        }
        taskForm.dataset.taskId = '';
        closeModal('taskModal');
        const data = await getProjectDetails(currentProjectId);
        displayProjectTasks(data.tasks);
    } catch (error) {
        showMessage(error.message || 'Failed to save task', 'error');
    }
}

async function openEditTaskModal(taskId) {
    try {
        const data = await getTaskDetails(taskId);
        const task = data.task;
        
        document.getElementById('taskModalTitle').textContent = 'Edit Task';
        document.getElementById('taskTitle').value = task.title;
        document.getElementById('taskDescription').value = task.description || '';
        document.getElementById('taskPriority').value = task.priority;
        document.getElementById('taskStatus').value = task.status;
        document.getElementById('taskDueDate').value = task.due_date || '';
        
        await loadTaskAssignees();
        document.getElementById('taskAssignee').value = task.assigned_to || '';
        
        // Store ID for update
        document.getElementById('taskForm').dataset.taskId = taskId;
        openModal('taskModal');
    } catch (error) {
        showMessage('Failed to load task', 'error');
    }
}

async function deleteTaskFromDetail(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        await deleteTask(taskId);
        showMessage('Task deleted successfully', 'success');
        const data = await getProjectDetails(currentProjectId);
        displayProjectTasks(data.tasks);
    } catch (error) {
        showMessage(error.message || 'Failed to delete task', 'error');
    }
}

async function loadUserTasks() {
    try {
        const data = await getUserTasks();
        displayUserTasks(data.tasks);
    } catch (error) {
        showMessage('Failed to load tasks', 'error');
    }
}

function displayUserTasks(tasks) {
    const container = document.getElementById('userTasksList');
    
    if (tasks.length === 0) {
        container.innerHTML = '<p class="empty-state">No tasks assigned to you</p>';
        return;
    }
    
    container.innerHTML = tasks.map(task => `
        <div class="task-card ${task.priority.toLowerCase()}-priority">
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    <span class="task-status ${task.status.toLowerCase()}">${task.status}</span>
                    <span>${escapeHtml(task.project_name)}</span>
                    ${task.due_date ? `<span>Due: ${formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
            <div class="task-actions">
                <button class="btn btn-small" onclick="updateTaskStatus(${task.id}, '${task.status}')">
                    ${task.status === 'Completed' ? 'Mark Pending' : 'Mark Done'}
                </button>
            </div>
        </div>
    `).join('');
}

async function updateTaskStatus(taskId, currentStatus) {
    const newStatus = currentStatus === 'Completed' ? 'Pending' : 'Completed';
    try {
        await updateTask(taskId, { status: newStatus });
        showMessage(`Task marked as ${newStatus}`, 'success');
        await loadUserTasks();
    } catch (error) {
        showMessage(error.message || 'Failed to update task', 'error');
    }
}

function filterUserTasks(status) {
    // Reload with filter
    if (status) {
        document.getElementById('userTasksList').innerHTML = '<p>Loading...</p>';
        getUserTasks(status).then(data => displayUserTasks(data.tasks)).catch(error => showMessage('Failed to filter tasks', 'error'));
    } else {
        loadUserTasks();
    }
}

// ===== MODAL HELPERS =====
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// ===== UTILITIES =====
function showMessage(text, type = 'error') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    setTimeout(() => {
        messageEl.className = 'message';
    }, 5000);
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function logoutUser() {
    if (!confirm('Are you sure you want to logout?')) return;
    
    try {
        await logout();
        window.location.href = 'index.html';
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = 'index.html';
    }
}

function showAddModal() {
    const section = document.querySelector('.content-section.active').id;
    if (section === 'projects') {
        showProjectModal();
    }
}
