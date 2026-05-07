# TaskFlow - Developer Quick Reference

## 🔨 Development Commands

### Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate
```

### Running
```bash
# Terminal 1: Backend
cd /Users/abhinav/Desktop/Project
python3 -m backend.app
# Backend runs on http://localhost:5001

# Terminal 2: Frontend
cd /Users/abhinav/Desktop/Project/frontend
python3 -m http.server 8000
# Frontend runs on http://localhost:8000
```

### Testing
```bash
# Test API health
curl http://localhost:5001/api/health

# Test signup
curl -X POST http://localhost:5001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123"}'
```

---

## 📁 Key File Locations

### Backend Files
- **app.py** - Main Flask application (REST APIs)
- **database.py** - Database models and functions

### Frontend Files
- **index.html** - Login/Signup page
- **dashboard.html** - Main application
- **styles.css** - All styling
- **api.js** - API client
- **auth.js** - Auth page logic
- **app.js** - Dashboard logic

### Documentation
- **README.md** - Full documentation
- **QUICKSTART.md** - 5-minute setup
- **TESTING.md** - Test results
- **DEPLOYMENT.md** - Production deployment
- **PROJECT_SUMMARY.md** - Project overview

---

## 🔑 API Endpoints Cheat Sheet

### Auth
```
POST   /api/auth/signup           # Register new user
POST   /api/auth/login            # Login user
POST   /api/auth/logout           # Logout user
GET    /api/auth/me               # Get current user
```

### Projects
```
POST   /api/projects              # Create project
GET    /api/projects              # List user projects
GET    /api/projects/<id>         # Get project details
PUT    /api/projects/<id>         # Update project
DELETE /api/projects/<id>         # Delete project
```

### Members
```
GET    /api/projects/<id>/members           # List members
POST   /api/projects/<id>/members           # Add member
DELETE /api/projects/<id>/members/<user_id> # Remove member
```

### Tasks
```
POST   /api/projects/<id>/tasks   # Create task
GET    /api/projects/<id>/tasks   # List project tasks
GET    /api/tasks/<id>            # Get task details
PUT    /api/tasks/<id>            # Update task
DELETE /api/tasks/<id>            # Delete task
```

### Dashboard
```
GET    /api/dashboard/stats       # Get statistics
GET    /api/dashboard/tasks       # Get user tasks
```

---

## 🗄️ Database Schema

### users
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  email TEXT,
  role TEXT DEFAULT 'Member',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### projects
```sql
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  owner_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

### project_members
```sql
CREATE TABLE project_members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  role TEXT DEFAULT 'Member',
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE(project_id, user_id)
);
```

### tasks
```sql
CREATE TABLE tasks (
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
);
```

---

## 🛠️ Common Tasks

### Add New API Endpoint
1. Add function in `backend/database.py`
2. Add route in `backend/app.py`
3. Add API call in `frontend/api.js`
4. Add UI in `frontend/dashboard.html`
5. Add logic in `frontend/app.js`

### Modify Database Schema
1. Edit schema in `backend/database.py`
2. Delete `project_management.db`
3. Restart backend (creates new DB)

### Update Styling
- Edit `frontend/styles.css`
- Changes apply immediately with page refresh

### Debug JavaScript
- Open browser DevTools (F12)
- Check Console tab for errors
- Use Network tab to see API calls

### Debug Python
- Check backend terminal output
- Add print statements in Flask routes
- Check `app.logger.info()` calls

---

## 🔐 Security Tips

### Passwords
- Currently: SHA256 (fine for demo)
- Production: Use bcrypt or Argon2

### Session
- Current: 7-day cookie
- Customize in `app.py` line 20

### CORS
- Currently: Allow all origins
- Production: Set specific domain in line 28

### SQL
- Using parameterized queries ✅
- No injection vulnerabilities ✅

---

## 📱 Frontend Structure

### app.js Functions
- `initApp()` - Initialize on page load
- `showSection(id)` - Switch sections
- `loadDashboard()` - Load dashboard data
- `loadProjects()` - Load projects list
- `loadUserTasks()` - Load user tasks
- `createProject()` - Create new project
- `createTask()` - Create new task
- `updateTask()` - Update task status
- `deleteProject()` - Delete project
- `showMessage()` - Show success/error

---

## 🧪 Testing Checklist

Before deployment, test:
- [ ] Signup with new user
- [ ] Login with credentials
- [ ] Logout and login again
- [ ] Create project
- [ ] View project details
- [ ] Add team member
- [ ] Create task
- [ ] Update task status
- [ ] Delete task
- [ ] Delete project
- [ ] Test on mobile browser
- [ ] Check console for errors

---

## 🚀 Performance Tips

1. **Database**
   - Add indexes: `CREATE INDEX idx_name ON table(column);`
   - Analyze queries: `EXPLAIN QUERY PLAN ...`

2. **Backend**
   - Use caching: `@cache.cached(timeout=300)`
   - Reduce database queries
   - Return only needed fields

3. **Frontend**
   - Minify CSS and JS
   - Lazy load images
   - Cache API responses
   - Debounce rapid requests

---

## 📊 Useful Queries

### Get user's projects with task counts
```sql
SELECT p.*, COUNT(t.id) as task_count
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
WHERE p.id IN (
  SELECT project_id FROM project_members
  WHERE user_id = ?
)
GROUP BY p.id;
```

### Get overdue tasks
```sql
SELECT * FROM tasks
WHERE status != 'Completed'
AND due_date < date('now');
```

### Get user stats
```sql
SELECT
  COUNT(*) as total_tasks,
  SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending
FROM tasks
WHERE assigned_to = ?;
```

---

## 🐛 Debugging Tips

### Backend Issues
```bash
# Check if port is in use
lsof -i :5001

# Kill process on port
kill -9 <PID>

# Enable Flask debug logging
export FLASK_DEBUG=1
python3 -m backend.app
```

### Frontend Issues
```bash
# Check browser console (F12)
# Check Network tab for failed requests
# Clear browser cache: Ctrl+Shift+Delete

# Check if backend is running
curl http://localhost:5001/api/health
```

### Database Issues
```bash
# View database with sqlite3
sqlite3 project_management.db

# List tables
.tables

# View schema
.schema

# Run query
SELECT * FROM users;

# Exit
.quit
```

---

## 📚 File Reading Order

For understanding the codebase:
1. `PROJECT_SUMMARY.md` (Overview)
2. `README.md` (Features)
3. `backend/database.py` (Data models)
4. `backend/app.py` (API endpoints)
5. `frontend/api.js` (API client)
6. `frontend/app.js` (App logic)
7. `frontend/styles.css` (Styling)

---

## 🎓 Learning Resources

### Python/Flask
- Flask documentation: https://flask.palletsprojects.com/
- SQLite3: https://www.sqlite.org/docs.html

### Frontend
- MDN Web Docs: https://developer.mozilla.org/
- JavaScript Fetch API: https://developer.mozilla.org/docs/Web/API/Fetch_API

### Database
- SQL Tutorial: https://www.w3schools.com/sql/
- Database Design: https://en.wikipedia.org/wiki/Database_design

---

## 💡 Pro Tips

1. **Keyboard Shortcuts**
   - Browser DevTools: F12 or Cmd+Option+I (Mac)
   - Reload: F5 or Cmd+R (Mac)
   - Hard reload: Ctrl+Shift+R or Cmd+Shift+R (Mac)

2. **Testing APIs**
   - Use curl for quick tests
   - Use Postman for complex requests
   - Check browser DevTools Network tab

3. **Code Organization**
   - Keep functions small and focused
   - Use meaningful variable names
   - Add comments for complex logic
   - Follow DRY (Don't Repeat Yourself)

4. **Performance**
   - Monitor API response times
   - Check database query times
   - Profile frontend performance
   - Use browser DevTools for analysis

---

## ✅ Deployment Checklist

- [ ] Update SECRET_KEY
- [ ] Switch to PostgreSQL (optional)
- [ ] Enable HTTPS
- [ ] Disable debug mode
- [ ] Configure CORS properly
- [ ] Setup logging
- [ ] Setup monitoring
- [ ] Test on staging
- [ ] Plan rollback
- [ ] Document deployment

---

## 📞 Quick Support

### Problem: 404 Not Found
**Solution**: Check URL, verify backend is running

### Problem: CORS Error
**Solution**: Verify backend is running on 5001, frontend on 8000

### Problem: Login not working
**Solution**: Check password is correct, verify database has users

### Problem: Page not loading
**Solution**: Check browser console, reload page, clear cache

### Problem: Database error
**Solution**: Delete `.db` file, restart backend

---

**Happy coding! 🚀**
