# TaskFlow - Quick Start Guide

Get TaskFlow up and running in 5 minutes!

## 🚀 Quick Setup

### Step 1: Install Dependencies (1 minute)
```bash
cd /Users/abhinav/Desktop/Project
pip3 install -r requirements.txt
```

### Step 2: Start Backend Server (Terminal 1)
```bash
cd /Users/abhinav/Desktop/Project
python3 -m backend.app
```

You should see:
```
✓ Database initialized successfully
 * Running on http://0.0.0.0:5001
```

### Step 3: Start Frontend Server (Terminal 2)
```bash
cd /Users/abhinav/Desktop/Project/frontend
python3 -m http.server 8000
```

You should see:
```
Serving HTTP on :: port 8000
```

### Step 4: Open in Browser
Open your browser and go to: **http://localhost:8000/index.html**

## 📝 Demo Flow (5 minutes)

### 1. Create Account (1 min)
1. Click "Sign Up"
2. Enter:
   - Username: `demo`
   - Email: `demo@example.com`
   - Password: `demo123456`
   - Confirm: `demo123456`
3. Click "Create Account" → Redirected to Dashboard

### 2. Create Project (1 min)
1. Click "Projects" in sidebar
2. Click "+ Create Project"
3. Enter:
   - Name: `My First Project`
   - Description: `Testing the TaskFlow app`
4. Click "Save Project"
5. Project appears in list

### 3. Create Task (1 min)
1. Click on the project card
2. Click "+ Create Task"
3. Fill in:
   - Title: `Setup Development Environment`
   - Description: `Install all dependencies and tools`
   - Priority: `High`
   - Status: `In Progress`
   - Due Date: Tomorrow's date
   - Assign To: `demo` (yourself)
4. Click "Save Task"

### 4. View Dashboard (1 min)
1. Click "Dashboard" in sidebar
2. See stats for your tasks
3. See recent tasks and projects

### 5. Test Task Filter (1 min)
1. Click "My Tasks" in sidebar
2. See your assigned tasks
3. Use filter dropdown to filter by status

## 🎯 Key Features to Explore

### Authentication
- ✅ Signup with username/password
- ✅ Login with credentials
- ✅ Logout with confirmation
- ✅ Session-based auth

### Projects
- ✅ Create new projects
- ✅ View all projects
- ✅ Edit project details
- ✅ Delete projects
- ✅ Add team members

### Tasks
- ✅ Create tasks with priority
- ✅ Set task status
- ✅ Assign to team members
- ✅ Set due dates
- ✅ Filter by status

### Dashboard
- ✅ View task statistics
- ✅ See overdue tasks
- ✅ Recent tasks list
- ✅ Projects overview

### Roles
- ✅ Admin: Full project control
- ✅ Member: Limited access
- ✅ Role-based permissions

## 🔑 Test Credentials

After signup, use your own credentials to login.

Example:
```
Username: demo
Password: demo123456
```

## 📱 Features Demo

### Multi-Tab Testing
Open multiple browser tabs at http://localhost:8000/dashboard.html and:
1. Create projects in one tab
2. See updates in other tabs
3. Try real-time collaboration

### Role Testing
1. Create first user with permissions
2. Create second user account
3. Add second user to your project
4. Test access controls

## 🐛 Troubleshooting

### Port 5001 Already in Use
```bash
# Find process on port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>
```

### Port 8000 Already in Use
```bash
# Use different port
python3 -m http.server 9000
# Then visit: http://localhost:9000/index.html
```

### Database Issues
```bash
# Reset database (deletes all data)
rm project_management.db

# Restart backend server - it will recreate fresh DB
python3 -m backend.app
```

### CORS Errors
- Ensure backend is running on port 5001
- Ensure frontend is on port 8000
- Check browser console for specific errors
- Try clearing browser cache

### Tasks Not Showing
- Refresh the page
- Check "My Tasks" section if assigned to you
- Verify task was created in project details

## 📚 Documentation Files

- **README.md** - Complete documentation
- **TESTING.md** - Detailed testing report
- **QUICKSTART.md** - This file

## 🎓 Learning Path

1. **Beginner**: Just signup, create a project, add tasks
2. **Intermediate**: Create multiple projects, add team members
3. **Advanced**: Test role-based access, manage permissions
4. **Developer**: Review code, understand API calls, modify features

## 🔧 File Structure

```
Project/
├── backend/
│   ├── app.py              # Main Flask app (5001)
│   ├── database.py         # SQLite functions
│   └── __init__.py         # Package init
├── frontend/
│   ├── index.html          # Login/Signup
│   ├── dashboard.html      # Main app
│   ├── styles.css          # All styling
│   ├── api.js              # API calls
│   ├── auth.js             # Auth logic
│   └── app.js              # App logic
├── requirements.txt         # Python packages
├── README.md               # Full docs
├── TESTING.md              # Test results
└── QUICKSTART.md           # This file
```

## 🚀 Next Steps

1. ✅ Try the demo flow above
2. ✅ Create multiple projects
3. ✅ Invite team members (create another account)
4. ✅ Manage tasks and track progress
5. ✅ Review code and customize
6. ✅ Deploy to production

## 💡 Tips

- Use meaningful project names and descriptions
- Set realistic due dates for tasks
- Assign tasks to team members for collaboration
- Check dashboard regularly for overview
- Use filters to focus on specific task statuses

## 📞 Support

If you encounter issues:
1. Check TESTING.md for known issues
2. Review README.md for configuration
3. Check browser console (F12) for errors
4. Verify backend is running on port 5001
5. Verify frontend is running on port 8000

## ⭐ Enjoy!

You're now ready to use TaskFlow! Start collaborating on projects and managing tasks efficiently.

Happy tasking! 🎉
