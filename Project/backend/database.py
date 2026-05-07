import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = 'project_management.db'

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT 'Member',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        owner_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users(id)
    )
    ''')
    
    # ProjectMembers table (for team management)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT DEFAULT 'Member',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(project_id, user_id)
    )
    ''')
    
    # Tasks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        assigned_to INTEGER,
        status TEXT DEFAULT 'Pending',
        priority TEXT DEFAULT 'Medium',
        due_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (assigned_to) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_value):
    """Verify password against hash"""
    return hash_password(password) == hash_value

# User functions
def create_user(username, password, email=None, role='Member'):
    """Create new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute('''
        INSERT INTO users (username, password_hash, email, role)
        VALUES (?, ?, ?, ?)
        ''', (username, password_hash, email, role))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {'id': user_id, 'username': username, 'email': email, 'role': role}
    except sqlite3.IntegrityError:
        return None

def get_user_by_username(username):
    """Get user by username"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_count():
    """Return total number of users"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM users')
    result = cursor.fetchone()
    conn.close()
    return result['total'] if result else 0

# Project functions
def create_project(name, owner_id, description=None):
    """Create new project"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO projects (name, description, owner_id)
    VALUES (?, ?, ?)
    ''', (name, description, owner_id))
    conn.commit()
    project_id = cursor.lastrowid
    
    # Add owner as member with Admin role
    cursor.execute('''
    INSERT INTO project_members (project_id, user_id, role)
    VALUES (?, ?, 'Admin')
    ''', (project_id, owner_id))
    conn.commit()
    conn.close()
    return {'id': project_id, 'name': name, 'description': description, 'owner_id': owner_id}

def get_project(project_id):
    """Get project by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    conn.close()
    return dict(project) if project else None

def get_user_projects(user_id):
    """Get all projects for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT p.* FROM projects p
    JOIN project_members pm ON p.id = pm.project_id
    WHERE pm.user_id = ?
    ORDER BY p.created_at DESC
    ''', (user_id,))
    projects = cursor.fetchall()
    conn.close()
    return [dict(p) for p in projects]

def update_project(project_id, name=None, description=None):
    """Update project"""
    conn = get_connection()
    cursor = conn.cursor()
    if name:
        cursor.execute('UPDATE projects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (name, project_id))
    if description:
        cursor.execute('UPDATE projects SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (description, project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    """Delete project and related data"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
    cursor.execute('DELETE FROM project_members WHERE project_id = ?', (project_id,))
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

# Project Members functions
def add_project_member(project_id, user_id, role='Member'):
    """Add member to project"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO project_members (project_id, user_id, role)
        VALUES (?, ?, ?)
        ''', (project_id, user_id, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def remove_project_member(project_id, user_id):
    """Remove member from project"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM project_members WHERE project_id = ? AND user_id = ?
    ''', (project_id, user_id))
    conn.commit()
    conn.close()

def get_project_members(project_id):
    """Get all members of a project"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT pm.*, u.username, u.email FROM project_members pm
    JOIN users u ON pm.user_id = u.id
    WHERE pm.project_id = ?
    ORDER BY pm.joined_at
    ''', (project_id,))
    members = cursor.fetchall()
    conn.close()
    return [dict(m) for m in members]

def get_user_role_in_project(project_id, user_id):
    """Get user's role in a project"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT role FROM project_members WHERE project_id = ? AND user_id = ?
    ''', (project_id, user_id))
    result = cursor.fetchone()
    conn.close()
    return result['role'] if result else None

# Task functions
def create_task(project_id, title, description=None, assigned_to=None, priority='Medium', due_date=None, status='Pending'):
    """Create new task"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO tasks (project_id, title, description, assigned_to, priority, due_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, title, description, assigned_to, priority, due_date, status))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {
        'id': task_id,
        'project_id': project_id,
        'title': title,
        'description': description,
        'assigned_to': assigned_to,
        'priority': priority,
        'due_date': due_date,
        'status': status
    }

def get_task(task_id):
    """Get task by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT t.*, u.username as assigned_to_name, p.name as project_name
    FROM tasks t
    LEFT JOIN users u ON t.assigned_to = u.id
    LEFT JOIN projects p ON t.project_id = p.id
    WHERE t.id = ?
    ''', (task_id,))
    task = cursor.fetchone()
    conn.close()
    return dict(task) if task else None

def get_project_tasks(project_id):
    """Get all tasks in a project"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT t.*, u.username as assigned_to_name FROM tasks t
    LEFT JOIN users u ON t.assigned_to = u.id
    WHERE t.project_id = ?
    ORDER BY t.created_at DESC
    ''', (project_id,))
    tasks = cursor.fetchall()
    conn.close()
    return [dict(t) for t in tasks]

def get_user_tasks(user_id):
    """Get all tasks assigned to a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT t.*, p.name as project_name FROM tasks t
    JOIN projects p ON t.project_id = p.id
    WHERE t.assigned_to = ?
    ORDER BY t.due_date ASC, t.created_at DESC
    ''', (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return [dict(t) for t in tasks]

def update_task(task_id, title=None, description=None, assigned_to=None, status=None, priority=None, due_date=None):
    """Update task"""
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    
    if title:
        updates.append('title = ?')
        params.append(title)
    if description is not None:
        updates.append('description = ?')
        params.append(description)
    if assigned_to is not None:
        updates.append('assigned_to = ?')
        params.append(assigned_to)
    if status:
        updates.append('status = ?')
        params.append(status)
    if priority:
        updates.append('priority = ?')
        params.append(priority)
    if due_date:
        updates.append('due_date = ?')
        params.append(due_date)
    
    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(task_id)
        query = 'UPDATE tasks SET ' + ', '.join(updates) + ' WHERE id = ?'
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()

def delete_task(task_id):
    """Delete task"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def get_dashboard_stats(user_id):
    """Get dashboard statistics for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get task stats
    cursor.execute('''
    SELECT 
        COUNT(*) as total_tasks,
        SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_tasks,
        SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_tasks,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks
    FROM tasks
    WHERE assigned_to = ?
    ''', (user_id,))
    
    stats = dict(cursor.fetchone())
    
    # Get overdue tasks
    cursor.execute('''
    SELECT COUNT(*) as overdue_tasks FROM tasks
    WHERE assigned_to = ? AND status != 'Completed' AND due_date < date('now')
    ''', (user_id,))
    
    overdue = dict(cursor.fetchone())
    stats.update(overdue)
    
    conn.close()
    return stats
