# Construction Management System - Complete Setup Guide

## 🏗️ System Overview

**3-Tier Access Control System:**
- **Admin Panel**: Full control - Create sites, projects, manage staff, assign permissions
- **Staff Panel**: Upload & manage their own documents (DPR, MOM, WPR, Photos)
- **User Panel**: Read-only access to view all sites, projects, and documents

**Document Types:**
- DPR (Daily Progress Report)
- MOM (Minutes of Meeting)
- WPR (Weekly Progress Report)
- Site Photos

---

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **PostgreSQL Database** (NeonDB recommended)
3. **Git** (optional, for version control)

---

## 🚀 Step-by-Step Installation

### Step 1: Database Setup (NeonDB)

1. Go to https://neon.tech and create a free account
2. Create a new project
3. Copy your connection string (looks like):
   ```
   postgresql://username:password@host/dbname?sslmode=require
   ```
4. Keep this connection string safe - you'll need it in Step 3

### Step 2: Download & Extract Project

1. Extract the `construction-cms` folder to your computer
2. Open terminal/command prompt in this folder

### Step 3: Environment Setup

1. Create a file named `.env` in the project root:
   ```bash
   touch .env
   ```

2. Edit `.env` and add your database URL:
   ```
   DATABASE_URL=postgresql://your-username:your-password@your-host/your-dbname?sslmode=require
   ```
   Replace with your actual NeonDB connection string from Step 1

### Step 4: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### Step 5: Initialize Database

```bash
# Run the application (it will auto-create tables)
python app.py
```

The application will:
- Create all necessary database tables
- Create a default admin account (username: `admin`, password: `admin123`)

### Step 6: Access the System

1. Open your browser and go to: `http://localhost:5000`
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`

**⚠️ IMPORTANT: Change the admin password immediately after first login!**

---

## 👥 User Management

### Creating Admin Accounts
Only the first admin can create more admins. To create additional admins:
1. Login as admin
2. Go to database and manually change a user's role to 'admin'

### Creating Staff Accounts
1. Admin Panel → Staff Management → Add Staff
2. Enter username, password, and full name
3. Staff member can now login and will see only their assigned projects

### Creating User Accounts (View-Only)
1. Admin Panel → Staff Management → Add User
2. Enter username, password, and full name
3. Users can view all sites and documents but cannot upload

### Assigning Staff to Projects
1. Admin Panel → Sites → Select Site → View Projects
2. Click "Assign Staff" on any project
3. Select staff members to assign
4. Assigned staff can now upload documents to this project

---

## 📁 Workflow

### Admin Workflow:
1. Create Sites (e.g., "Downtown Tower", "Highway Project")
2. Create Projects under each site (e.g., "Foundation Work", "Floor 1-5")
3. Create Staff accounts
4. Assign staff to specific projects
5. Monitor all documents across all projects

### Staff Workflow:
1. Login with credentials provided by admin
2. View assigned projects only
3. Upload documents (DPR, MOM, WPR, Photos) to assigned projects
4. Can only view and edit their own uploaded documents
5. Cannot see other staff members' documents

### User Workflow:
1. Login with credentials provided by admin
2. Browse all sites
3. View all projects
4. View all documents (organized by type)
5. Download documents
6. Cannot upload or modify anything

---

## 🔒 Security Features

1. **Password Hashing**: All passwords stored using Werkzeug's secure hashing
2. **Session Management**: Secure session-based authentication
3. **Role-Based Access Control**: Strict separation of admin/staff/user permissions
4. **File Upload Validation**: Only allowed file types accepted
5. **SQL Injection Protection**: All queries use parameterized statements
6. **Access Verification**: Every route checks user permissions
7. **Document Isolation**: Staff can only see/edit their own documents

---

## 🌐 Deployment to Production

### Option 1: Render.com (Recommended - Free)

1. Create account on https://render.com
2. Create new Web Service
3. Connect your GitHub repository (or upload code)
4. Set environment variables:
   ```
   DATABASE_URL = your-neondb-connection-string
   ```
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python app.py`
7. Deploy!

### Option 2: Railway.app

1. Create account on https://railway.app
2. New Project → Deploy from GitHub
3. Add NeonDB connection string as environment variable
4. Railway will auto-detect Flask and deploy

### Option 3: Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL (or use NeonDB)
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variable if using NeonDB
heroku config:set DATABASE_URL=your-neondb-url

# Deploy
git push heroku main

# Initialize database
heroku run python app.py
```

### Option 4: VPS (DigitalOcean, Linode, AWS)

```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip nginx -y

# Clone/upload project
# Install dependencies
pip3 install -r requirements.txt

# Set environment variables
export DATABASE_URL=your-neondb-url

# Install Gunicorn
pip3 install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# For production, setup Nginx as reverse proxy and use systemd for auto-restart
```

---

## 📂 Project Structure

```
construction-cms/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── static/
│   ├── css/
│   │   └── style.css          # All styling
│   ├── js/
│   │   └── script.js          # JavaScript functionality
│   └── uploads/               # Uploaded documents (auto-created)
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── login.html             # Login page
│   ├── dashboard.html         # Dashboard for all roles
│   ├── admin/                 # Admin-only templates
│   │   ├── sites.html
│   │   ├── add_site.html
│   │   ├── site_projects.html
│   │   ├── add_project.html
│   │   ├── staff.html
│   │   ├── add_staff.html
│   │   ├── add_user.html
│   │   └── assign_staff.html
│   ├── staff/                 # Staff-only templates
│   │   ├── projects.html
│   │   ├── project_documents.html
│   │   └── upload_document.html
│   └── user/                  # User (view-only) templates
│       ├── sites.html
│       ├── site_projects.html
│       └── project_documents.html
└── database/                  # (auto-managed by PostgreSQL)
```

---

## 🔧 Configuration

### Allowed File Types
Edit `app.py` line 13 to change allowed file extensions:
```python
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}
```

### Max Upload Size
Edit `app.py` line 12:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### Secret Key
For production, change the secret key in `app.py` line 11:
```python
app.secret_key = 'your-very-secure-random-string-here'
```

---

## 🐛 Troubleshooting

### Database Connection Error
- Check your DATABASE_URL in .env file
- Ensure NeonDB is active and accessible
- Verify connection string format

### File Upload Not Working
- Check `static/uploads` folder exists and has write permissions
- Verify file size is under 16MB
- Check file extension is in allowed list

### Login Issues
- Clear browser cookies/cache
- Check database has user records
- Verify password hashing is working

### Permission Denied Errors
- Check user role is correct in database
- Verify session is active
- Try logging out and back in

---

## 📊 Database Schema

### users table
- id, username, password_hash, full_name, role, is_active, created_at

### sites table
- id, site_name, location, description, created_by, created_at, is_active

### projects table
- id, project_name, site_id, description, start_date, created_by, created_at, is_active

### documents table
- id, project_id, document_type, title, file_path, uploaded_by, upload_date, description, report_date

### staff_assignments table
- id, staff_id, project_id, assigned_by, assigned_at

---

## 🎯 Default Login Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change this immediately after first login!**

To change admin password:
1. Go to database
2. Generate new hash: `python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('newpassword'))"`
3. Update: `UPDATE users SET password_hash = 'new-hash' WHERE username = 'admin'`

---

## 📞 Support & Maintenance

### Backup Database
NeonDB provides automatic backups. For manual backup:
```bash
pg_dump DATABASE_URL > backup.sql
```

### Update Application
```bash
git pull origin main
pip install -r requirements.txt --upgrade
# Restart server
```

### Monitor Logs
Check Flask console output for errors and access logs

---

## 🎓 Training Guide for Users

### For Admins:
1. Master site and project creation
2. Learn staff assignment workflow
3. Understand access control
4. Regular database backups

### For Staff:
1. Know your assigned projects
2. Understand document types (DPR vs MOM vs WPR)
3. Regular document uploads
4. Use descriptive titles and dates

### For Users:
1. Navigate site structure
2. Filter documents by type
3. Download reports for review
4. Understand project timelines

---

## 🔐 Security Best Practices

1. ✅ Change default admin password immediately
2. ✅ Use strong passwords for all accounts
3. ✅ Regular database backups
4. ✅ HTTPS in production (handled by hosting platforms)
5. ✅ Keep dependencies updated
6. ✅ Monitor access logs
7. ✅ Limit admin accounts
8. ✅ Regular security audits

---

## 📈 Future Enhancements (Optional)

- Email notifications for new documents
- Advanced search and filtering
- Document version control
- Mobile app
- Real-time collaboration
- Analytics dashboard
- Export reports to PDF
- Calendar integration
- Task management
- Budget tracking

---

**System developed for Construction Industry Document Management**
**Version 1.0 - Production Ready**
