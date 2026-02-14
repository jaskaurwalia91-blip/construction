# Construction CMS - Quick Start Guide (Hindi/Hinglish)

## 🚀 Jaldi Setup Kaise Kare

### Step 1: Database Banao (NeonDB)
1. https://neon.tech pe jao
2. Sign up karo (free hai)
3. New project banao
4. Connection string copy karo (ye dikehga):
   ```
   postgresql://username:password@host/dbname
   ```

### Step 2: Project Setup
```bash
# Folder mein jao
cd construction-cms

# Dependencies install karo
pip install -r requirements.txt
```

### Step 3: Database URL Set Karo
1. `.env.example` file ko copy karke `.env` banao:
   ```bash
   cp .env.example .env
   ```

2. `.env` file edit karo aur apna NeonDB URL daalo:
   ```
   DATABASE_URL=postgresql://your-actual-connection-string
   ```

### Step 4: Application Chalo
```bash
python app.py
```

### Step 5: Browser Mein Kholo
1. Browser mein jao: `http://localhost:5000`
2. Login karo:
   - Username: `admin`
   - Password: `admin123`

## 📱 Kaise Use Kare

### Admin Ke Liye:
1. **Sites Banao**: Admin Panel → Sites → Add New Site
2. **Projects Banao**: Site select karo → Add Project
3. **Staff Add Karo**: Staff Management → Add Staff
4. **Staff Assign Karo**: Project mein jao → Assign Staff

### Staff Ke Liye:
1. Login karo apne credentials se
2. "My Projects" mein apne assigned projects dikhengy
3. "Upload Document" pe click karke files upload karo
4. Document type select karo (DPR/MOM/WPR/Photos)

### User Ke Liye:
1. Login karo
2. "Browse Sites" → Site select karo
3. Projects dekho
4. Documents view/download karo

## 🔒 Security

### Password Change Kaise Kare:
```python
# Python console mein run karo
from werkzeug.security import generate_password_hash
print(generate_password_hash('new_password'))
# Output copy karke database mein update karo
```

### Default Admin Password ZAROOR Change Karo!

## 🌐 Online Deploy Kaise Kare (Render.com - Free)

1. **GitHub pe Code Daalo**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/username/construction-cms.git
   git push -u origin main
   ```

2. **Render.com pe Jao**:
   - https://render.com pe sign up karo
   - "New Web Service" click karo
   - GitHub repo connect karo
   - Settings mein jao:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python app.py`
     - Environment Variables add karo:
       - Key: `DATABASE_URL`
       - Value: Apna NeonDB connection string

3. **Deploy Click Karo** - 5 minutes mein live ho jayega!

## 📂 Files Structure

```
construction-cms/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── .env               # Database config (banao ye)
├── README.md          # English documentation
├── QUICK_START_HI.md  # Ye file (Hindi guide)
├── static/
│   ├── css/           # Styling
│   ├── js/            # JavaScript
│   └── uploads/       # Documents store honge yahan
└── templates/         # HTML pages
    ├── admin/         # Admin pages
    ├── staff/         # Staff pages
    └── user/          # User pages
```

## 🎯 Document Types

1. **DPR**: Daily Progress Report - Har din ka kaam
2. **MOM**: Minutes of Meeting - Meeting notes
3. **WPR**: Weekly Progress Report - Hafta report
4. **Photos**: Site ki photos

## ⚠️ Common Problems & Solutions

### Database connect nahi ho raha?
- `.env` file check karo
- NeonDB connection string sahi hai verify karo
- Internet connection check karo

### File upload nahi ho rahi?
- File size 16MB se kam hai check karo
- File type allowed hai (PDF, DOC, JPG, PNG, XLS)
- `static/uploads` folder exists karta hai check karo

### Login nahi ho raha?
- Username/password sahi hai?
- Browser cookies clear karo
- Database mein user exist karta hai?

## 💡 Tips

1. ✅ Pehle admin password change karo
2. ✅ Strong passwords use karo
3. ✅ Regular backup lo (NeonDB automatic backup deta hai)
4. ✅ Staff ko sirf zaruri projects assign karo
5. ✅ Document titles clear rakho
6. ✅ Report dates zaroor daalo

## 📞 Help Chahiye?

1. README.md padho (detailed English documentation)
2. Code comments padho
3. Error messages dhyan se padho
4. Database logs check karo

## 🎓 Training Points

### Admin Training (2 hours):
- Sites aur projects kaise banaye
- Staff management
- Assignments kaise kare
- Security best practices

### Staff Training (1 hour):
- Login process
- Document upload kaise kare
- Document types samajhna
- Apne documents manage karna

### User Training (30 minutes):
- Login karna
- Sites browse karna
- Documents dekhna/download karna

---

**🏗️ Construction Industry ke liye Professional Document Management System**

Koi doubt ho toh README.md file dekho - usme sab kuch detail mein hai!
