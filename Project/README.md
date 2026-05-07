# TaskFlow - Project Management Web App

A complete web application for managing projects and tasks with role-based access control.

## Features

✅ **Authentication**
- User registration (signup)
- User login with username and password
- Session management
- Role-based access (Admin/Member)

✅ **Project Management**
- Create, view, update, and delete projects
- Team member management
- Assign roles to team members

✅ **Task Management**
- Create tasks with priority levels (Low, Medium, High)
- Assign tasks to team members
- Track task status (Pending, In Progress, Completed)
- Set due dates
- Filter tasks by status

✅ **Dashboard**
- View task statistics
- See recent tasks
- Monitor overdue tasks
- Projects overview

## Tech Stack

### Backend
- **Framework**: Python 3 with Flask
- **Database**: SQLite (SQL)
- **API**: REST APIs with JSON
- **Authentication**: Session-based with password hashing

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design
- **JavaScript**: Vanilla JS (no frameworks)
- **API Client**: Fetch API

## Project Structure

```
Project/
├── backend/
│   ├── app.py                 # Flask application with REST APIs
│   └── database.py            # Database models and functions
├── frontend/
│   ├── index.html             # Login/Signup page
│   ├── dashboard.html         # Main dashboard
│   ├── styles.css             # All styling
│   ├── api.js                 # API call functions
│   ├── auth.js                # Authentication logic
│   └── app.js                 # Dashboard application logic
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation & Setup

### Prerequisites
- Python 3.7+
- macOS, Linux, or Windows
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Install Dependencies

```bash
cd Project
pip install -r requirements.txt
```

### Step 2: Start the Backend Server

```bash
cd Project
python3 -m backend.app
```

The server will start at `http://localhost:5001`

You should see:
```
✓ Database initialized successfully
 * Running on http://0.0.0.0:5001
```

### Step 3: Open Frontend in Browser

Open `frontend/index.html` in your web browser:
```bash
# Option 1: Direct file opening (may have CORS issues)
open frontend/index.html

# Option 2: Use Python's simple HTTP server (Recommended)
cd Project/frontend
python -m http.server 8000
# Then open http://localhost:8000 in browser
```

## Usage

### First Time User

1. **Create Account**
   - Click "Sign Up" on the login page
   - Enter username (min 3 chars), email (optional), password (min 6 chars)
   - Click "Create Account"
   - You'll be redirected to the dashboard

2. **Login**
   - Enter your username and password
   - Click "Sign In"

### Dashboard Features

**📊 Dashboard Tab**
- View task statistics (total, pending, in progress, completed, overdue)
- See recent tasks
- Browse projects overview

**📁 Projects Tab**
- View all your projects
- Click "+ Create Project" to add new project
- Click on a project to view details, manage members, and create tasks
- Edit or delete projects (if you're the owner)

**✓ My Tasks Tab**
- View all tasks assigned to you
- Filter by status (All, Pending, In Progress, Completed)
- Mark tasks as done or pending
- Sort by due date

### Role-Based Access

**Admin**
- Full control over project
- Create/edit/delete tasks
- Add/remove team members
- Edit project details

**Member**
- View project and tasks
- Update assigned tasks
- Cannot delete project or remove members

## Database Schema

### users
```sql
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- password_hash (TEXT)
- email (TEXT)
- role (TEXT) - 'Admin' or 'Member'
- created_at (TIMESTAMP)
```

### projects
```sql
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- description (TEXT)
- owner_id (INTEGER) - references users.id
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### project_members
```sql
- id (INTEGER PRIMARY KEY)
- project_id (INTEGER) - references projects.id
- user_id (INTEGER) - references users.id
- role (TEXT) - 'Admin' or 'Member'
- joined_at (TIMESTAMP)
```

### tasks
```sql
- id (INTEGER PRIMARY KEY)
- project_id (INTEGER) - references projects.id
- title (TEXT)
- description (TEXT)
- assigned_to (INTEGER) - references users.id (nullable)
- status (TEXT) - 'Pending', 'In Progress', 'Completed'
- priority (TEXT) - 'Low', 'Medium', 'High'
- due_date (DATE)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

## REST API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info

### Projects
- `POST /api/projects` - Create new project
- `GET /api/projects` - Get user's projects
- `GET /api/projects/<id>` - Get project details
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project

### Project Members
- `GET /api/projects/<id>/members` - List project members
- `POST /api/projects/<id>/members` - Add member to project
- `DELETE /api/projects/<id>/members/<user_id>` - Remove member

### Tasks
- `POST /api/projects/<id>/tasks` - Create task
- `GET /api/projects/<id>/tasks` - Get project tasks
- `GET /api/tasks/<id>` - Get task details
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/tasks` - Get user's tasks

## Testing the Application

### Test Scenario 1: Basic Authentication
1. Signup with username "john", password "password123"
2. Logout
3. Login with the same credentials
4. Verify you're redirected to dashboard

### Test Scenario 2: Project Management
1. Create a project "Web App Project"
2. Add description
3. Add a team member (create another account first)
4. Verify member is added with "Member" role

### Test Scenario 3: Task Management
1. Create a task "Design Homepage" in the project
2. Set priority to "High"
3. Assign to a team member
4. Set due date to tomorrow
5. View task in "My Tasks" if assigned to you
6. Update task status to "In Progress"
7. Mark as "Completed"

### Test Scenario 4: Dashboard
1. Create multiple tasks with different statuses
2. Verify dashboard shows correct statistics
3. Check overdue calculation

## Troubleshooting

### CORS Error
- Ensure backend is running on `http://localhost:5001`
- Check that CORS is enabled in `app.py`
- Frontend should be served from `http://localhost:8000` or opened as file

### Database Lock Error
- Delete `project_management.db` to reset database
- Make sure only one backend instance is running

### Session Not Working
- Check browser cookies are enabled
- Verify session secret key is set in `app.py`
- Browser should allow credentials in fetch requests

### Tasks Not Showing
- Verify tasks are assigned to current user
- Check task status in database
- Refresh browser if data is stale

## Development Notes

### Adding New Features

1. **Database Changes**
   - Modify schema in `backend/database.py`
   - Create migration or delete db to reinitialize

2. **New API Endpoint**
   - Add route in `backend/app.py`
   - Create database function in `backend/database.py`
   - Add API call in `frontend/api.js`

3. **UI Changes**
   - Update HTML in `frontend/dashboard.html`
   - Add CSS to `frontend/styles.css`
   - Add JavaScript logic in `frontend/app.js`

### Security Considerations

- Passwords are hashed with SHA256
- Consider using bcrypt for production
- Session timeout should be configured
- HTTPS should be used in production
- Input validation is implemented
- SQL injection is prevented with parameterized queries

## Future Enhancements

- Task comments and collaboration
- File attachments for tasks
- Email notifications
- Task templates
- Progress tracking with Gantt charts
- Team analytics and reports
- Dark mode
- Mobile app
- Real-time updates with WebSockets

## License

MIT License - Feel free to use for learning and personal projects

## Support

For issues or questions, create an issue in the repository or contact the development team.
