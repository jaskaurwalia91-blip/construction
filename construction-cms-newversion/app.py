from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import secrets
import tempfile

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Fix for Render deployment - use temp directory for file uploads
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}

# Database Configuration (NeonDB)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_5h0nTNEfpOLH@ep-soft-credit-aimmm2c4.us-east-1.aws.neon.tech/neondb?sslmode=require')

def get_db():
    """Get database connection"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cur = conn.cursor()
    
    # Users table (Admin and Staff)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(200) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'staff', 'user')),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sites table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id SERIAL PRIMARY KEY,
            site_name VARCHAR(200) NOT NULL,
            location VARCHAR(300),
            description TEXT,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Projects table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            project_name VARCHAR(200) NOT NULL,
            site_id INTEGER REFERENCES sites(id) ON DELETE CASCADE,
            description TEXT,
            start_date DATE,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Documents table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            document_type VARCHAR(50) NOT NULL CHECK (document_type IN ('DPR', 'MOM', 'WPR', 'PHOTO')),
            title VARCHAR(300) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            uploaded_by INTEGER REFERENCES users(id),
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            report_date DATE
        )
    ''')
    
    # Staff assignments table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS staff_assignments (
            id SERIAL PRIMARY KEY,
            staff_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            assigned_by INTEGER REFERENCES users(id),
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(staff_id, project_id)
        )
    ''')
    
    # Create default admin if not exists
    cur.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        admin_hash = generate_password_hash('admin123')
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
            ('admin', admin_hash, 'Administrator', 'admin')
        )
    
    conn.commit()
    cur.close()
    conn.close()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(role=None):
    """Decorator to protect routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first', 'error')
                return redirect(url_for('login'))
            
            if role and session.get('role') != role:
                flash('Access denied', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND is_active = TRUE", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            flash(f'Welcome {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required()
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role == 'admin':
        # Admin sees all sites and projects
        cur.execute("SELECT COUNT(*) as count FROM sites WHERE is_active = TRUE")
        sites_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM projects WHERE is_active = TRUE")
        projects_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM users WHERE role = 'staff' AND is_active = TRUE")
        staff_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM documents")
        documents_count = cur.fetchone()['count']
        
        stats = {
            'sites': sites_count,
            'projects': projects_count,
            'staff': staff_count,
            'documents': documents_count
        }
        
    elif role == 'staff':
        # Staff sees their assigned projects
        cur.execute("""
            SELECT COUNT(DISTINCT sa.project_id) as count 
            FROM staff_assignments sa 
            WHERE sa.staff_id = %s
        """, (user_id,))
        projects_count = cur.fetchone()['count']
        
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM documents d
            WHERE d.uploaded_by = %s
        """, (user_id,))
        documents_count = cur.fetchone()['count']
        
        stats = {
            'projects': projects_count,
            'documents': documents_count
        }
        
    else:  # user role
        # User sees total counts
        cur.execute("SELECT COUNT(*) as count FROM sites WHERE is_active = TRUE")
        sites_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM projects WHERE is_active = TRUE")
        projects_count = cur.fetchone()['count']
        
        stats = {
            'sites': sites_count,
            'projects': projects_count
        }
    
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', stats=stats)

# ==================== ADMIN ROUTES ====================

@app.route('/admin/sites')
@login_required(role='admin')
def admin_sites():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.*, u.full_name as created_by_name 
        FROM sites s 
        LEFT JOIN users u ON s.created_by = u.id 
        WHERE s.is_active = TRUE
        ORDER BY s.created_at DESC
    """)
    sites = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/sites.html', sites=sites)

@app.route('/admin/sites/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_site():
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        location = request.form.get('location')
        description = request.form.get('description')
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sites (site_name, location, description, created_by) VALUES (%s, %s, %s, %s)",
            (site_name, location, description, session['user_id'])
        )
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Site added successfully', 'success')
        return redirect(url_for('admin_sites'))
    
    return render_template('admin/add_site.html')

@app.route('/admin/sites/<int:site_id>/projects')
@login_required(role='admin')
def admin_site_projects(site_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM sites WHERE id = %s", (site_id,))
    site = cur.fetchone()
    
    cur.execute("""
        SELECT p.*, u.full_name as created_by_name 
        FROM projects p 
        LEFT JOIN users u ON p.created_by = u.id 
        WHERE p.site_id = %s AND p.is_active = TRUE
        ORDER BY p.created_at DESC
    """, (site_id,))
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/site_projects.html', site=site, projects=projects)

@app.route('/admin/projects/add/<int:site_id>', methods=['GET', 'POST'])
@login_required(role='admin')
def add_project(site_id):
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO projects (project_name, site_id, description, start_date, created_by) VALUES (%s, %s, %s, %s, %s)",
            (project_name, site_id, description, start_date, session['user_id'])
        )
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Project added successfully', 'success')
        return redirect(url_for('admin_site_projects', site_id=site_id))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sites WHERE id = %s", (site_id,))
    site = cur.fetchone()
    cur.close()
    conn.close()
    
    return render_template('admin/add_project.html', site=site)

@app.route('/admin/staff')
@login_required(role='admin')
def admin_staff():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE role IN ('staff', 'user') ORDER BY created_at DESC")
    staff_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/staff.html', staff_list=staff_list)

@app.route('/admin/staff/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_staff():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        conn = get_db()
        cur = conn.cursor()
        
        # Check if username exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash('Username already exists', 'error')
        else:
            password_hash = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
                (username, password_hash, full_name, 'staff')
            )
            conn.commit()
            flash('Staff member added successfully', 'success')
            cur.close()
            conn.close()
            return redirect(url_for('admin_staff'))
        
        cur.close()
        conn.close()
    
    return render_template('admin/add_staff.html')

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash('Username already exists', 'error')
        else:
            password_hash = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
                (username, password_hash, full_name, 'user')
            )
            conn.commit()
            flash('User added successfully', 'success')
            cur.close()
            conn.close()
            return redirect(url_for('admin_staff'))
        
        cur.close()
        conn.close()
    
    return render_template('admin/add_user.html')

@app.route('/admin/projects/<int:project_id>/assign', methods=['GET', 'POST'])
@login_required(role='admin')
def assign_staff(project_id):
    if request.method == 'POST':
        staff_ids = request.form.getlist('staff_ids')
        
        conn = get_db()
        cur = conn.cursor()
        
        for staff_id in staff_ids:
            try:
                cur.execute(
                    "INSERT INTO staff_assignments (staff_id, project_id, assigned_by) VALUES (%s, %s, %s)",
                    (staff_id, project_id, session['user_id'])
                )
            except:
                pass  # Already assigned
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Staff assigned successfully', 'success')
        return redirect(url_for('admin_site_projects', site_id=request.args.get('site_id')))
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cur.fetchone()
    
    cur.execute("SELECT * FROM users WHERE role = 'staff' AND is_active = TRUE")
    staff_list = cur.fetchall()
    
    cur.execute("SELECT staff_id FROM staff_assignments WHERE project_id = %s", (project_id,))
    assigned_staff = [row['staff_id'] for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return render_template('admin/assign_staff.html', project=project, staff_list=staff_list, assigned_staff=assigned_staff)

@app.route('/admin/documents')
@login_required(role='admin')
def admin_all_documents():
    conn = get_db()
    cur = conn.cursor()
    
    # Get all sites for filter
    cur.execute("SELECT id, site_name FROM sites WHERE is_active = TRUE ORDER BY site_name")
    sites = cur.fetchall()
    
    # Build query based on filters
    doc_type = request.args.get('doc_type', '')
    site_id = request.args.get('site_id', '')
    
    query = """
        SELECT d.*, 
               p.project_name, 
               s.site_name,
               u.full_name as uploaded_by_name
        FROM documents d
        JOIN projects p ON d.project_id = p.id
        JOIN sites s ON p.site_id = s.id
        LEFT JOIN users u ON d.uploaded_by = u.id
        WHERE 1=1
    """
    params = []
    
    if doc_type:
        query += " AND d.document_type = %s"
        params.append(doc_type)
    
    if site_id:
        query += " AND s.id = %s"
        params.append(int(site_id))
    
    query += " ORDER BY d.upload_date DESC LIMIT 500"
    
    cur.execute(query, params)
    documents = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/all_documents.html', documents=documents, sites=sites)

# ==================== STAFF ROUTES ====================

@app.route('/staff/projects')
@login_required(role='staff')
def staff_projects():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.*, s.site_name 
        FROM projects p
        JOIN sites s ON p.site_id = s.id
        JOIN staff_assignments sa ON p.id = sa.project_id
        WHERE sa.staff_id = %s AND p.is_active = TRUE
        ORDER BY p.created_at DESC
    """, (session['user_id'],))
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('staff/projects.html', projects=projects)

@app.route('/staff/projects/<int:project_id>/documents')
@login_required(role='staff')
def staff_project_documents(project_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Verify staff is assigned to this project
    cur.execute(
        "SELECT * FROM staff_assignments WHERE staff_id = %s AND project_id = %s",
        (session['user_id'], project_id)
    )
    if not cur.fetchone():
        flash('Access denied', 'error')
        return redirect(url_for('staff_projects'))
    
    cur.execute("""
        SELECT p.*, s.site_name 
        FROM projects p
        JOIN sites s ON p.site_id = s.id
        WHERE p.id = %s
    """, (project_id,))
    project = cur.fetchone()
    
    cur.execute("""
        SELECT d.*, u.full_name as uploaded_by_name
        FROM documents d
        LEFT JOIN users u ON d.uploaded_by = u.id
        WHERE d.project_id = %s AND d.uploaded_by = %s
        ORDER BY d.upload_date DESC
    """, (project_id, session['user_id']))
    documents = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('staff/project_documents.html', project=project, documents=documents)

@app.route('/staff/upload/<int:project_id>', methods=['GET', 'POST'])
@login_required(role='staff')
def staff_upload_document(project_id):
    if request.method == 'POST':
        document_type = request.form.get('document_type')
        title = request.form.get('title')
        description = request.form.get('description')
        report_date = request.form.get('report_date')
        file = request.files.get('file')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(upload_path)
                
                conn = get_db()
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO documents (project_id, document_type, title, file_path, uploaded_by, description, report_date) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (project_id, document_type, title, filename, session['user_id'], description, report_date)
                )
                conn.commit()
                cur.close()
                conn.close()
                
                flash('Document uploaded successfully', 'success')
                return redirect(url_for('staff_project_documents', project_id=project_id))
            except Exception as e:
                flash(f'Error uploading file: {str(e)}', 'error')
        else:
            flash('Invalid file type', 'error')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cur.fetchone()
    cur.close()
    conn.close()
    
    return render_template('staff/upload_document.html', project=project)

@app.route('/staff/documents/<int:doc_id>/delete', methods=['POST'])
@login_required(role='staff')
def staff_delete_document(doc_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM documents WHERE id = %s AND uploaded_by = %s", (doc_id, session['user_id']))
    document = cur.fetchone()
    
    if document:
        # Delete file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], document['file_path'])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        cur.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
        conn.commit()
        flash('Document deleted successfully', 'success')
    else:
        flash('Access denied', 'error')
    
    cur.close()
    conn.close()
    
    return redirect(request.referrer or url_for('staff_projects'))

# ==================== USER ROUTES ====================

@app.route('/user/sites')
@login_required(role='user')
def user_sites():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sites WHERE is_active = TRUE ORDER BY created_at DESC")
    sites = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('user/sites.html', sites=sites)

@app.route('/user/sites/<int:site_id>/projects')
@login_required(role='user')
def user_site_projects(site_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM sites WHERE id = %s", (site_id,))
    site = cur.fetchone()
    
    cur.execute("""
        SELECT * FROM projects 
        WHERE site_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
    """, (site_id,))
    projects = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('user/site_projects.html', site=site, projects=projects)

@app.route('/user/projects/<int:project_id>/documents')
@login_required(role='user')
def user_project_documents(project_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.*, s.site_name 
        FROM projects p
        JOIN sites s ON p.site_id = s.id
        WHERE p.id = %s
    """, (project_id,))
    project = cur.fetchone()
    
    cur.execute("""
        SELECT d.*, u.full_name as uploaded_by_name
        FROM documents d
        LEFT JOIN users u ON d.uploaded_by = u.id
        WHERE d.project_id = %s
        ORDER BY d.upload_date DESC
    """, (project_id,))
    documents = cur.fetchall()
    
    # Group documents by type
    docs_by_type = {
        'DPR': [],
        'MOM': [],
        'WPR': [],
        'PHOTO': []
    }
    
    for doc in documents:
        docs_by_type[doc['document_type']].append(doc)
    
    cur.close()
    conn.close()
    
    return render_template('user/project_documents.html', project=project, docs_by_type=docs_by_type)

# ==================== FILE DOWNLOAD ====================

@app.route('/uploads/<filename>')
@login_required()
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
