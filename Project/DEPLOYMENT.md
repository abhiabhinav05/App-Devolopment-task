# TaskFlow - Production Deployment Guide

Complete guide to deploy TaskFlow to production.

## 🌐 Deployment Options

### Option 1: Cloud Deployment (Recommended)

#### Heroku Deployment

1. **Setup Heroku Account**
   ```bash
   # Install Heroku CLI
   brew tap heroku/brew && brew install heroku
   
   # Login
   heroku login
   ```

2. **Prepare for Heroku**
   ```bash
   # Update requirements.txt with production server
   echo "gunicorn==20.1.0" >> requirements.txt
   
   # Create Procfile
   echo "web: gunicorn backend.app:app" > Procfile
   
   # Create runtime.txt
   echo "python-3.9.16" > runtime.txt
   ```

3. **Deploy**
   ```bash
   # Create app
   heroku create taskflow-app
   
   # Set environment variables
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key-here
   
   # Deploy
   git push heroku main
   
   # Check logs
   heroku logs --tail
   ```

#### AWS Deployment

1. **EC2 Instance Setup**
   ```bash
   # Launch Ubuntu 20.04 LTS instance
   # Connect via SSH
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python
   sudo apt install python3 python3-pip python3-venv -y
   
   # Clone repository
   git clone <your-repo> taskflow
   cd taskflow
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Setup Nginx + Gunicorn**
   ```bash
   # Install Nginx
   sudo apt install nginx -y
   
   # Install Gunicorn
   pip install gunicorn
   
   # Create systemd service
   sudo nano /etc/systemd/system/taskflow.service
   ```

   Add:
   ```
   [Unit]
   Description=TaskFlow Application
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/taskflow
   Environment="PATH=/home/ubuntu/taskflow/venv/bin"
   ExecStart=/home/ubuntu/taskflow/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 backend.app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Enable and start service
   sudo systemctl enable taskflow
   sudo systemctl start taskflow
   ```

3. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/taskflow
   ```

   Add:
   ```
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /static {
           alias /home/ubuntu/taskflow/frontend;
       }
   }
   ```

   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/taskflow /etc/nginx/sites-enabled/
   
   # Test config
   sudo nginx -t
   
   # Start Nginx
   sudo systemctl restart nginx
   ```

### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt gunicorn
   
   COPY . .
   
   ENV FLASK_ENV=production
   ENV SECRET_KEY=your-secret-key
   
   EXPOSE 5001
   
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "backend.app:app"]
   ```

2. **Create Docker Compose**
   ```yaml
   version: '3.8'
   
   services:
     backend:
       build: .
       ports:
         - "5001:5001"
       environment:
         FLASK_ENV: production
         SECRET_KEY: ${SECRET_KEY}
       volumes:
         - ./project_management.db:/app/project_management.db
     
     frontend:
       image: nginx:alpine
       ports:
         - "8000:80"
       volumes:
         - ./frontend:/usr/share/nginx/html
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

### Option 3: VPS Deployment (DigitalOcean, Linode, etc.)

Follow the AWS EC2 instructions as they're similar.

## 🔒 Security Configuration

### 1. Environment Variables
```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=generate-random-secret-key
DATABASE_URL=postgresql://user:pass@localhost/taskflow
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
EOF
```

### 2. Update Backend Configuration
```python
# backend/app.py modifications
import os
from dotenv import load_dotenv

load_dotenv()

app.secret_key = os.getenv('SECRET_KEY', 'default-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

### 3. Database Migration
Switch from SQLite to PostgreSQL:

```bash
# Install psycopg2
pip install psycopg2-binary

# Create PostgreSQL database
sudo -u postgres createdb taskflow

# Update database.py to use PostgreSQL
```

### 4. SSL/TLS Certificate
```bash
# Using Let's Encrypt (Free)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d yourdomain.com
sudo certbot renew --dry-run
```

### 5. Update Nginx for HTTPS
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Rest of config...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📊 Performance Optimization

### 1. Frontend Optimization
```bash
# Minify CSS
npm install -g cssnano
cssnano styles.css -o styles.min.css

# Minify JavaScript
npm install -g uglify-js
uglifyjs app.js -c -m -o app.min.js
```

### 2. Backend Optimization
```python
# Add caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/projects')
@cache.cached(timeout=300)
def get_projects():
    # Implementation
    pass
```

### 3. Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_project_members_project_id ON project_members(project_id);
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
```

### 4. Load Balancing
```nginx
upstream backend {
    least_conn;
    server backend1:5001;
    server backend2:5001;
    server backend3:5001;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
    }
}
```

## 🔄 Continuous Integration/Deployment

### GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: pytest tests/
    
    - name: Deploy to Heroku
      if: github.ref == 'refs/heads/main'
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
        heroku_app_name: "taskflow-app"
        heroku_email: "your-email@example.com"
```

## 📈 Monitoring & Logging

### 1. Application Logging
```python
# backend/app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/taskflow.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('TaskFlow startup')
```

### 2. Error Tracking (Sentry)
```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()]
)
```

### 3. Uptime Monitoring
- Use UptimeRobot (free tier available)
- Set up health check endpoint
- Get email alerts on downtime

## 🔄 Backup & Recovery

### Automated Backup
```bash
# Daily database backup script
#!/bin/bash
BACKUP_DIR="/backups/taskflow"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump taskflow > $BACKUP_DIR/taskflow_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/taskflow_$DATE.sql s3://your-bucket/backups/

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete
```

### Disaster Recovery
```bash
# Restore from backup
pg_restore < backup_file.sql
```

## ✅ Pre-Deployment Checklist

- [ ] Update SECRET_KEY to secure random value
- [ ] Switch to PostgreSQL
- [ ] Enable HTTPS/SSL
- [ ] Set Flask debug mode to False
- [ ] Configure CORS for production domain
- [ ] Setup logging
- [ ] Test all APIs
- [ ] Verify database backups
- [ ] Setup monitoring
- [ ] Configure rate limiting
- [ ] Enable GZIP compression
- [ ] Test on staging environment first
- [ ] Plan rollback strategy
- [ ] Document deployment steps
- [ ] Setup alerts

## 🚀 Deployment Commands

### Deploy to AWS EC2
```bash
# Connect to instance
ssh -i key.pem ubuntu@your-instance-ip

# Pull latest code
cd ~/taskflow
git pull origin main

# Restart service
sudo systemctl restart taskflow

# Check status
sudo systemctl status taskflow
```

### Deploy to Heroku
```bash
# Push to production
git push heroku main

# View logs
heroku logs --tail

# Scale dyos
heroku ps:scale web=2
```

### Deploy with Docker
```bash
docker-compose pull
docker-compose up -d --force-recreate
docker-compose exec backend python -m flask db upgrade
```

## 📞 Support

For deployment issues:
1. Check logs: `tail -f logs/taskflow.log`
2. Test health endpoint: `curl http://localhost:5001/api/health`
3. Verify database connection
4. Check network and firewall settings
5. Review deployment configuration

---

**Ready to deploy?** Start with Option 1 (Heroku) for fastest setup, or Option 2 (Docker) for flexibility!
