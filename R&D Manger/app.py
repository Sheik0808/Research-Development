import os
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========= MOTIVATIONAL QUOTES =========
MOTIVATIONAL_QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal. - Winston Churchill",
    "Your research today shapes tomorrow's discoveries.",
    "Every great achievement starts with a single publication.",
    "Knowledge is power, and your research shares that power.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "Excellence is not a destination; it's a continuous journey.",
    "Great minds discuss ideas, average minds discuss events. - Eleanor Roosevelt",
    "Your contribution to research matters more than you know.",
    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
    "The only limit to our realization is our doubt. - Franklin D. Roosevelt",
    "Dream big, work hard, stay focused!",
    "Your research could inspire the next generation of scientists.",
    "Believe you can, and you're halfway there. - Theodore Roosevelt",
    "The best time to plant a tree was 20 years ago. The second best is now.",
]

# ========= VISION & MISSION =========
VISION = """
To be a leading institution in fostering innovation and excellence in research and development, 
contributing to the advancement of knowledge and society through collaborative academic endeavors.
"""

MISSION = """
Our mission is to:
• Promote high-quality research and academic publications
• Support faculty and students in their research endeavors
• Track and manage research output effectively
• Foster a culture of continuous learning and innovation
• Collaborate with national and international research communities
• Contribute to societal development through groundbreaking research
"""

# -------- DATABASE ----------------
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        with open('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# -------- REWARDS SYSTEM --------
def award_credits(user_id, action, credits, description):
    """Award credits to user for specific actions"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO rewards (user_id, action, credits_earned, description) VALUES (?, ?, ?, ?)',
        (user_id, action, credits, description)
    )
    conn.execute('UPDATE users SET credits = credits + ? WHERE id = ?', (credits, user_id))
    conn.commit()
    conn.close()

def get_user_credits(user_id):
    """Get total credits for a user"""
    conn = get_db_connection()
    result = conn.execute('SELECT credits FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result['credits'] if result else 0

def get_random_quote():
    """Get a random motivational quote"""
    return random.choice(MOTIVATIONAL_QUOTES)

# -------- LOGIN DECORATOR --------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- ROUTES ----------------
# ========= AUTHENTICATION ROUTES =========

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                session['is_first_visit'] = True
                
                # Log the login time
                conn = get_db_connection()
                conn.execute("""
                    INSERT INTO login_logs (user_id, username, full_name, role, login_time)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (user['id'], user['username'], user['full_name'], user['role']))
                conn.commit()
                conn.close()
                
                # Route to appropriate dashboard based on role
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('dashboard'))

        return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        department = request.form.get('department')
        designation = request.form.get('designation')
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not full_name:
            error = 'Full name is required.'
        elif not role:
            error = 'Role is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'

        if error is None:
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO users (username, email, password, role, full_name, department, designation) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (username, email, generate_password_hash(password), role, full_name, department, designation)
                )
                conn.commit()
                conn.close()
                # Store signup info in session for welcome page
                session['signup_full_name'] = full_name
                session['signup_role'] = role
                return redirect(url_for('registration_success'))
            except sqlite3.IntegrityError as e:
                if 'username' in str(e):
                    error = 'Username already exists.'
                elif 'email' in str(e):
                    error = 'Email already registered.'
                else:
                    error = 'Registration failed. Please try again.'
            finally:
                conn.close()

        return render_template('signup.html', error=error)

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ========= REGISTRATION SUCCESS PAGE =========
@app.route('/registration-success')
def registration_success():
    full_name = session.pop('signup_full_name', 'User')
    role = session.pop('signup_role', 'faculty')
    motivational_quote = get_random_quote()
    
    return render_template('registration_success.html',
                         full_name=full_name,
                         role=role,
                         motivational_quote=motivational_quote)

# ========= VISION & MISSION ROUTE =========
@app.route('/vision-mission')
def vision_mission():
    return render_template('vision_mission.html', vision=VISION, mission=MISSION)

# ========= PROTECTED ROUTES =========
@app.route('/')
@login_required
def dashboard():
    conn = get_db_connection()
    
    # Total journals count
    total_journals = conn.execute('SELECT COUNT(*) FROM journals').fetchone()[0]
    
    # Total reports (assuming reports = distinct entries)
    total_reports = total_journals
    
    # Get professor/author publication statistics
    professor_stats = conn.execute("""
        SELECT author_name, COUNT(*) as paper_count
        FROM journals
        WHERE author_name IS NOT NULL AND author_name != ''
        GROUP BY author_name
        ORDER BY paper_count DESC
        LIMIT 10
    """).fetchall()
    
    # Get department statistics
    dept_stats = conn.execute("""
        SELECT department, COUNT(*) as paper_count
        FROM journals
        WHERE department IS NOT NULL AND department != ''
        GROUP BY department
        ORDER BY paper_count DESC
    """).fetchall()
    
    # Get indexing statistics
    indexing_stats = {
        'scopus': conn.execute('SELECT COUNT(*) FROM journals WHERE is_scopus = 1').fetchone()[0],
        'sci': conn.execute('SELECT COUNT(*) FROM journals WHERE is_sci_scie_ssci = 1').fetchone()[0],
        'wos': conn.execute('SELECT COUNT(*) FROM journals WHERE is_wos = 1').fetchone()[0]
    }
    
    conn.close()
    
    # Get user credits and random quote
    user_credits = get_user_credits(session['user_id'])
    motivational_quote = get_random_quote()
    is_first_visit = session.pop('is_first_visit', False)
    
    return render_template('dashboard.html', 
                         total_journals=total_journals,
                         total_reports=total_reports,
                         professor_stats=professor_stats,
                         dept_stats=dept_stats,
                         indexing_stats=indexing_stats,
                         user_credits=user_credits,
                         motivational_quote=motivational_quote,
                         is_first_visit=is_first_visit)

# ========= ADMIN DASHBOARD =========
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Check if user is admin
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    
    # Get overall statistics
    total_journals = conn.execute('SELECT COUNT(*) FROM journals').fetchone()[0]
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_faculty = conn.execute('SELECT COUNT(*) FROM users WHERE role = "faculty"').fetchone()[0]
    total_students = conn.execute('SELECT COUNT(*) FROM users WHERE role = "student"').fetchone()[0]
    total_credits_distributed = conn.execute('SELECT COALESCE(SUM(credits), 0) FROM users').fetchone()[0]
    
    # Get top performers
    top_performers = conn.execute("""
        SELECT full_name, credits, department, role
        FROM users
        WHERE credits > 0
        ORDER BY credits DESC
        LIMIT 10
    """).fetchall()
    
    # Get all publishers data
    all_publishers = conn.execute("""
        SELECT 
            u.id,
            u.full_name,
            u.email,
            u.role,
            u.department,
            u.credits,
            COUNT(j.id) as publication_count
        FROM users u
        LEFT JOIN journals j ON u.full_name LIKE '%' || j.author_name || '%' OR j.author_name LIKE '%' || u.full_name || '%'
        GROUP BY u.id
        ORDER BY u.credits DESC
    """).fetchall()
    
    # Get department statistics
    dept_stats = conn.execute("""
        SELECT department, COUNT(*) as paper_count
        FROM journals
        WHERE department IS NOT NULL AND department != ''
        GROUP BY department
        ORDER BY paper_count DESC
    """).fetchall()
    
    # Get indexing statistics
    indexing_stats = {
        'scopus': conn.execute('SELECT COUNT(*) FROM journals WHERE is_scopus = 1').fetchone()[0],
        'sci': conn.execute('SELECT COUNT(*) FROM journals WHERE is_sci_scie_ssci = 1').fetchone()[0],
        'wos': conn.execute('SELECT COUNT(*) FROM journals WHERE is_wos = 1').fetchone()[0]
    }
    
    conn.close()
    
    is_first_visit = session.pop('is_first_visit', False)
    motivational_quote = get_random_quote()
    
    return render_template('admin_dashboard.html',
                         total_journals=total_journals,
                         total_users=total_users,
                         total_faculty=total_faculty,
                         total_students=total_students,
                         total_credits_distributed=total_credits_distributed,
                         top_performers=top_performers,
                         all_publishers=all_publishers,
                         dept_stats=dept_stats,
                         indexing_stats=indexing_stats,
                         motivational_quote=motivational_quote,
                         is_first_visit=is_first_visit)

# ---------------- ADD JOURNAL ----------------
@app.route('/add_journal', methods=['GET', 'POST'])
@login_required
def add_journal():
    if request.method == 'POST':

        # 1️⃣ Collect form data (MATCHES HTML + DB)
        data = (
            request.form.get('journal_status'),
            request.form.get('department'),
            request.form.get('author_position'),
            request.form.get('author_name'),
            request.form.get('collaborative_authors'),

            request.form.get('paper_title'),
            request.form.get('publisher'),
            request.form.get('journal_name'),
            request.form.get('journal_scope'),
            request.form.get('vol_issue_page'),
            request.form.get('month_year'),
            request.form.get('issn_number'),

            1 if 'is_scopus' in request.form else 0,
            1 if 'is_sci' in request.form else 0,
            1 if 'is_wos' in request.form else 0,

            request.form.get('impact_factor'),
            request.form.get('citation_score'),
            request.form.get('sjr_rating'),
            request.form.get('h_index'),
            request.form.get('anna_univ_list'),

            request.form.get('preview_link'),
            request.form.get('home_page_link'),
            request.form.get('doi_link'),

            request.form.get('collab_scope'),
            request.form.get('collab_institution'),

            ""  # proof filename placeholder
        )

        # 2️⃣ File upload
        proof_file = request.files.get('proof')
        filename = ""
        if proof_file and proof_file.filename != "":
            filename = secure_filename(proof_file.filename)
            proof_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data = data[:-1] + (filename,)

        # 3️⃣ Insert into database
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO journals (
                journal_status, department, author_position, author_name, collaborative_authors,
                paper_title, publisher, journal_name, journal_scope, vol_issue_page,
                month_year, issn_number,
                is_scopus, is_sci_scie_ssci, is_wos,
                impact_factor, citation_score, sjr_rating, h_index, anna_univ_list,
                preview_link, home_page_link, doi_link,
                collab_scope, collab_institution,
                proof_filename
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, data)

        conn.commit()
        conn.close()
        
        # Award credits for adding a publication
        credits_earned = 50
        award_credits(
            session['user_id'],
            'publication_added',
            credits_earned,
            f"Added publication: {request.form.get('paper_title', 'Untitled')}"
        )
        
        # Store publication info in session for thank you page
        session['publication_title'] = request.form.get('paper_title', 'Your Publication')
        session['credits_earned'] = credits_earned
        
        return redirect(url_for('thank_you'))

    return render_template('add_journal.html')

# ========= THANK YOU PAGE =========
@app.route('/thank-you')
@login_required
def thank_you():
    publication_title = session.pop('publication_title', 'Your Publication')
    credits_earned = session.pop('credits_earned', 50)
    user_credits = get_user_credits(session['user_id'])
    motivational_quote = get_random_quote()
    
    return render_template('thank_you.html',
                         publication_title=publication_title,
                         credits_earned=credits_earned,
                         user_credits=user_credits,
                         motivational_quote=motivational_quote)

# ---------------- VIEW JOURNALS ----------------
@app.route('/view_journals')
@login_required
def view_journals():
    conn = get_db_connection()
    journals = conn.execute('SELECT * FROM journals').fetchall()
    conn.close()
    return render_template('view_journals.html', journals=journals)

# ========= LOGIN HISTORY ROUTE =========
@app.route('/login-history')
@login_required
def login_history():
    # Only admin can view all login history, users see their own
    conn = get_db_connection()
    
    if session.get('role') == 'admin':
        # Admin sees all login logs
        login_logs = conn.execute("""
            SELECT * FROM login_logs 
            ORDER BY login_time DESC 
            LIMIT 100
        """).fetchall()
        title = "All Login History"
    else:
        # Regular users see only their own login logs
        login_logs = conn.execute("""
            SELECT * FROM login_logs 
            WHERE user_id = ? 
            ORDER BY login_time DESC 
            LIMIT 50
        """, (session['user_id'],)).fetchall()
        title = "Your Login History"
    
    conn.close()
    return render_template('login_history.html', login_logs=login_logs, title=title)

# ---------------- RUN ----------------
if __name__ == '__main__':
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=True)
