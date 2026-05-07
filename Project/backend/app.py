from flask import Flask, request, jsonify, session
from flask_cors import CORS
from functools import wraps
import os
import sys
from datetime import timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database functions
from backend.database import (
    init_db, create_user, get_user_by_username, get_user_by_id, get_user_count, verify_password,
    create_project, get_project, get_user_projects, update_project, delete_project,
    add_project_member, remove_project_member, get_project_members, get_user_role_in_project,
    create_task, get_task, get_project_tasks, get_user_tasks, update_task, delete_task,
    get_dashboard_stats
)

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_in_production'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

CORS(app, supports_credentials=True)

# Middleware for authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        user = get_user_by_id(session['user_id'])
        if user['role'] != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register new user"""
    data = request.json
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    if len(data['username']) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    default_role = 'Admin' if get_user_count() == 0 else 'Member'
    user = create_user(
        username=data['username'],
        password=data['password'],
        email=data.get('email'),
        role=default_role
    )
    
    if not user:
        return jsonify({'error': 'Username already exists'}), 409
    
    session.permanent = True
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    return jsonify({
        'message': 'Signup successful',
        'user': user
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = get_user_by_username(data['username'])
    
    if not user or not verify_password(data['password'], user['password_hash']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    session.permanent = True
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user info"""
    user = get_user_by_id(session['user_id'])
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role']
    }), 200

# ==================== PROJECT ENDPOINTS ====================

@app.route('/api/projects', methods=['POST'])
@login_required
def create_new_project():
    """Create new project"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'Project name required'}), 400
    
    project = create_project(
        name=data['name'],
        owner_id=session['user_id'],
        description=data.get('description')
    )
    
    return jsonify({
        'message': 'Project created successfully',
        'project': project
    }), 201

@app.route('/api/projects', methods=['GET'])
@login_required
def list_user_projects():
    """Get all projects for current user"""
    projects = get_user_projects(session['user_id'])
    return jsonify({
        'projects': projects,
        'count': len(projects)
    }), 200

@app.route('/api/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project_details(project_id):
    """Get project details"""
    project = get_project(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check if user is member of project
    role = get_user_role_in_project(project_id, session['user_id'])
    if not role and project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    members = get_project_members(project_id)
    tasks = get_project_tasks(project_id)
    
    return jsonify({
        'project': project,
        'members': members,
        'tasks': tasks,
        'user_role': role or 'Admin'
    }), 200

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project_details(project_id):
    """Update project"""
    project = get_project(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check if user is admin of project
    role = get_user_role_in_project(project_id, session['user_id'])
    if role != 'Admin' and project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Only admin can update project'}), 403
    
    data = request.json
    update_project(project_id, data.get('name'), data.get('description'))
    
    updated_project = get_project(project_id)
    return jsonify({
        'message': 'Project updated successfully',
        'project': updated_project
    }), 200

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project_endpoint(project_id):
    """Delete project"""
    project = get_project(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Only owner can delete
    if project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Only owner can delete project'}), 403
    
    delete_project(project_id)
    return jsonify({'message': 'Project deleted successfully'}), 200

# ==================== PROJECT MEMBERS ENDPOINTS ====================

@app.route('/api/projects/<int:project_id>/members', methods=['GET'])
@login_required
def list_project_members(project_id):
    """Get project members"""
    project = get_project(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    role = get_user_role_in_project(project_id, session['user_id'])
    if not role and project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    members = get_project_members(project_id)
    return jsonify({
        'members': members,
        'count': len(members)
    }), 200

@app.route('/api/projects/<int:project_id>/members', methods=['POST'])
@login_required
def add_project_member_endpoint(project_id):
    """Add member to project"""
    project = get_project(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check if user is admin of project
    role = get_user_role_in_project(project_id, session['user_id'])
    if role != 'Admin' and project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Only admin can add members'}), 403
    
    data = request.json
    
    if not data.get('username'):
        return jsonify({'error': 'Username required'}), 400
    
    user = get_user_by_username(data['username'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if add_project_member(project_id, user['id'], data.get('role', 'Member')):
        return jsonify({'message': 'Member added successfully'}), 201
    else:
        return jsonify({'error': 'Member already exists in project'}), 409

@app.route('/api/projects/<int:project_id>/members/<int:member_id>', methods=['DELETE'])
@login_required
def remove_project_member_endpoint(project_id, member_id):
    """Remove member from project"""
    project = get_project(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check if user is admin of project
    role = get_user_role_in_project(project_id, session['user_id'])
    if role != 'Admin' and project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Only admin can remove members'}), 403
    
    remove_project_member(project_id, member_id)
    return jsonify({'message': 'Member removed successfully'}), 200

# ==================== TASK ENDPOINTS ====================

@app.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
@login_required
def create_new_task(project_id):
    """Create new task"""
    project = get_project(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    role = get_user_role_in_project(project_id, session['user_id'])
    if not role and project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    
    if not data.get('title'):
        return jsonify({'error': 'Task title required'}), 400
    
    assigned_to = data.get('assigned_to')
    if assigned_to == '':
        assigned_to = None
    if assigned_to is not None:
        assigned_to = int(assigned_to)
        assigned_role = get_user_role_in_project(project_id, assigned_to)
        if not assigned_role and get_user_by_id(assigned_to) is None:
            return jsonify({'error': 'Assigned user not found'}), 404
        if not assigned_role and project['owner_id'] != assigned_to:
            return jsonify({'error': 'Assignee must be a project member'}), 400
    
    task = create_task(
        project_id=project_id,
        title=data['title'],
        description=data.get('description'),
        assigned_to=assigned_to,
        priority=data.get('priority', 'Medium'),
        due_date=data.get('due_date'),
        status=data.get('status', 'Pending')
    )
    
    return jsonify({
        'message': 'Task created successfully',
        'task': task
    }), 201

@app.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
@login_required
def list_project_tasks(project_id):
    """Get all tasks in project"""
    project = get_project(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check if user is member of project
    role = get_user_role_in_project(project_id, session['user_id'])
    if not role and project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    tasks = get_project_tasks(project_id)
    return jsonify({
        'tasks': tasks,
        'count': len(tasks)
    }), 200

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task_details(task_id):
    """Get task details"""
    task = get_task(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check if user is member of project or assigned to task
    role = get_user_role_in_project(task['project_id'], session['user_id'])
    if not role and task['assigned_to'] != session['user_id']:
        project = get_project(task['project_id'])
        if project['owner_id'] != session['user_id']:
            return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'task': task}), 200

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task_endpoint(task_id):
    """Update task"""
    task = get_task(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    role = get_user_role_in_project(task['project_id'], session['user_id'])
    if not role:
        project = get_project(task['project_id'])
        if project['owner_id'] != session['user_id'] and task['assigned_to'] != session['user_id']:
            return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    assigned_to = data.get('assigned_to')
    if assigned_to == '':
        assigned_to = None
    if assigned_to is not None:
        assigned_to = int(assigned_to)
        assigned_role = get_user_role_in_project(task['project_id'], assigned_to)
        if not assigned_role and get_user_by_id(assigned_to) is None:
            return jsonify({'error': 'Assigned user not found'}), 404
        if not assigned_role and task['project_id'] and get_project(task['project_id'])['owner_id'] != assigned_to:
            return jsonify({'error': 'Assignee must be a project member'}), 400

    update_task(
        task_id,
        title=data.get('title'),
        description=data.get('description'),
        assigned_to=assigned_to,
        status=data.get('status'),
        priority=data.get('priority'),
        due_date=data.get('due_date')
    )
    
    updated_task = get_task(task_id)
    return jsonify({
        'message': 'Task updated successfully',
        'task': updated_task
    }), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task_endpoint(task_id):
    """Delete task"""
    task = get_task(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check if user is admin of project
    project = get_project(task['project_id'])
    role = get_user_role_in_project(task['project_id'], session['user_id'])
    
    if role != 'Admin' and project['owner_id'] != session['user_id']:
        return jsonify({'error': 'Only admin can delete task'}), 403
    
    delete_task(task_id)
    return jsonify({'message': 'Task deleted successfully'}), 200

# ==================== DASHBOARD ENDPOINTS ====================

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():
    """Get dashboard statistics"""
    stats = get_dashboard_stats(session['user_id'])
    tasks = get_user_tasks(session['user_id'])
    projects = get_user_projects(session['user_id'])
    
    return jsonify({
        'stats': stats,
        'recent_tasks': tasks[:10],
        'projects': projects
    }), 200

@app.route('/api/dashboard/tasks', methods=['GET'])
@login_required
def dashboard_tasks():
    """Get user's tasks"""
    tasks = get_user_tasks(session['user_id'])
    
    # Filter by status if provided
    status_filter = request.args.get('status')
    if status_filter:
        tasks = [t for t in tasks if t['status'] == status_filter]
    
    return jsonify({
        'tasks': tasks,
        'count': len(tasks)
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)
