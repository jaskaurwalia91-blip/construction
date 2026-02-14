# 🚀 DEPLOYMENT CHECKLIST - Construction CMS

## Pre-Deployment Steps

### ✅ 1. Database Setup (NeonDB)
- [ ] Create NeonDB account at https://neon.tech
- [ ] Create new project/database
- [ ] Copy connection string
- [ ] Test connection locally

### ✅ 2. Code Preparation
- [ ] All files present in project folder
- [ ] `.env` file created with DATABASE_URL
- [ ] Test locally: `python app.py`
- [ ] Login works with admin/admin123
- [ ] Create test site, project, staff
- [ ] Upload test document
- [ ] Verify all 3 user roles work

### ✅ 3. Security Check
- [ ] Change default admin password
- [ ] Review `app.secret_key` (should be random)
- [ ] Check file upload restrictions
- [ ] Test role-based access control

---

## DEPLOYMENT OPTION 1: Render.com (Recommended - Free)

### Steps:
1. **GitHub Setup**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   # Create repo on GitHub
   git remote add origin https://github.com/yourusername/construction-cms.git
   git push -u origin main
   ```

2. **Render.com Setup**:
   - Go to https://render.com
   - Sign up/Login
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Configure:
     - **Name**: construction-cms
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Instance Type**: Free

3. **Environment Variables**:
   - Click "Environment" tab
   - Add:
     - Key: `DATABASE_URL`
     - Value: Your NeonDB connection string

4. **Deploy**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Access at: `https://construction-cms.onrender.com`

### Post-Deployment:
- [ ] Test login
- [ ] Change admin password
- [ ] Create real admin account
- [ ] Delete test data

---

## DEPLOYMENT OPTION 2: Railway.app

1. **Setup**:
   - Go to https://railway.app
   - Login with GitHub
   - "New Project" → "Deploy from GitHub repo"
   - Select repository

2. **Configure**:
   - Railway auto-detects Python
   - Add environment variable:
     - `DATABASE_URL`: Your NeonDB URL
   
3. **Deploy**:
   - Auto-deploys on push
   - Get URL from Railway dashboard

---

## DEPLOYMENT OPTION 3: Heroku

```bash
# Install Heroku CLI
# Windows: Download from heroku.com
# Mac: brew install heroku/brew/heroku
# Linux: curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-construction-cms

# Set environment variable
heroku config:set DATABASE_URL=your-neondb-url

# Deploy
git push heroku main

# Open app
heroku open
```

---

## DEPLOYMENT OPTION 4: VPS (DigitalOcean/Linode)

### Server Setup:
```bash
# Connect to server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install python3 python3-pip nginx git -y

# Clone project
git clone https://github.com/yourusername/construction-cms.git
cd construction-cms

# Install Python packages
pip3 install -r requirements.txt

# Install Gunicorn
pip3 install gunicorn

# Create .env file
nano .env
# Add: DATABASE_URL=your-neondb-url
# Save: Ctrl+X, Y, Enter
```

### Run Application:
```bash
# Test run
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Setup as Service (Auto-restart):
```bash
# Create service file
sudo nano /etc/systemd/system/construction-cms.service
```

Add this:
```ini
[Unit]
Description=Construction CMS
After=network.target

[Service]
User=root
WorkingDirectory=/root/construction-cms
Environment="DATABASE_URL=your-neondb-url"
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable construction-cms
sudo systemctl start construction-cms
sudo systemctl status construction-cms
```

### Setup Nginx Reverse Proxy:
```bash
sudo nano /etc/nginx/sites-available/construction-cms
```

Add this:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /root/construction-cms/static;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/construction-cms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Setup SSL (Free HTTPS):
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## POST-DEPLOYMENT CHECKLIST

### Security:
- [ ] Change admin password immediately
- [ ] Create strong passwords for all accounts
- [ ] Enable HTTPS (automatic on Render/Railway/Heroku)
- [ ] Set up regular database backups
- [ ] Monitor access logs

### Functionality:
- [ ] Test all 3 user roles (admin, staff, user)
- [ ] Test file upload (all document types)
- [ ] Test file download
- [ ] Test staff assignment
- [ ] Test document deletion
- [ ] Test on mobile devices

### Data:
- [ ] Delete all test data
- [ ] Create production sites
- [ ] Create production projects
- [ ] Create staff accounts
- [ ] Assign staff to projects
- [ ] Train users

### Monitoring:
- [ ] Set up uptime monitoring (UptimeRobot - free)
- [ ] Configure error notifications
- [ ] Regular database backups
- [ ] Monitor disk space (uploads folder)

---

## BACKUP STRATEGY

### Automated Backups (NeonDB):
NeonDB provides automatic daily backups. No action needed.

### Manual Backup:
```bash
# Download database backup
pg_dump DATABASE_URL > backup-$(date +%Y%m%d).sql

# Compress
gzip backup-$(date +%Y%m%d).sql
```

### Restore from Backup:
```bash
# Uncompress
gunzip backup-20240101.sql.gz

# Restore
psql DATABASE_URL < backup-20240101.sql
```

### File Backups (Uploads):
```bash
# Zip uploads folder
zip -r uploads-backup-$(date +%Y%m%d).zip static/uploads/

# Download to local machine
scp user@server:/path/uploads-backup.zip ./
```

---

## MAINTENANCE

### Weekly:
- [ ] Check application logs
- [ ] Monitor disk space
- [ ] Review uploaded documents
- [ ] Check for failed uploads

### Monthly:
- [ ] Update dependencies: `pip install -r requirements.txt --upgrade`
- [ ] Security audit
- [ ] Performance review
- [ ] User feedback collection

### Quarterly:
- [ ] Full system backup
- [ ] Disaster recovery test
- [ ] Security review
- [ ] Feature planning

---

## TROUBLESHOOTING

### App Won't Start:
```bash
# Check logs
heroku logs --tail  # For Heroku
# Or check Render/Railway dashboard

# Common fixes:
# 1. Verify DATABASE_URL is set correctly
# 2. Check requirements.txt is complete
# 3. Verify Python version compatibility
```

### Database Connection Failed:
```bash
# Test connection
python3 -c "import psycopg2; conn = psycopg2.connect('DATABASE_URL'); print('Success!')"

# If fails:
# 1. Check NeonDB is active
# 2. Verify connection string
# 3. Check firewall rules
```

### File Upload Issues:
```bash
# Check permissions
ls -la static/uploads/

# Fix permissions
chmod 755 static/uploads/

# Check disk space
df -h
```

---

## SCALING CONSIDERATIONS

### When to Upgrade:
- More than 100 concurrent users
- Database size > 1GB
- More than 10,000 documents

### Scaling Options:
1. **Database**: Upgrade NeonDB plan
2. **Storage**: Use cloud storage (AWS S3, Cloudinary)
3. **App**: Increase instance size/count
4. **CDN**: Add CloudFlare for static files

---

## CONTACT & SUPPORT

For deployment issues:
1. Check README.md
2. Review error logs
3. Verify environment variables
4. Test locally first
5. Check documentation on hosting platform

---

**🏗️ System Ready for Production Deployment**

Choose deployment option based on:
- **Render.com**: Easiest, free tier available
- **Railway.app**: Good for small teams
- **Heroku**: Established platform, good documentation
- **VPS**: Full control, best for large deployments
