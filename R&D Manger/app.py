import os
import sqlite3
import random
import requests
import re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
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

# ---------------- FETCH DOI DATA ----------------
@app.route('/fetch_doi', methods=['POST'])
@login_required
def fetch_doi():
    """Fetch publication details from DOI using CrossRef API"""
    try:
        doi_input = request.json.get('doi', '').strip()
        
        if not doi_input:
            return jsonify({'success': False, 'error': 'DOI is required'}), 400
        
        # Extract DOI from URL if full URL is provided
        doi = doi_input
        if 'doi.org/' in doi_input:
            doi = doi_input.split('doi.org/')[-1]
        
        # Clean up DOI
        doi = doi.strip('/')
        
        # Fetch from CrossRef API
        api_url = f'https://api.crossref.org/works/{doi}'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'DOI not found or invalid'}), 404
        
        data = response.json()['message']
        
        # Extract relevant information
        paper_data = {
            'success': True,
            'paper_title': data.get('title', [''])[0] if data.get('title') else '',
            'journal_name': data.get('container-title', [''])[0] if data.get('container-title') else '',
            'publisher': data.get('publisher', ''),
            'doi_link': f"https://doi.org/{doi}",
            'issn_number': data.get('ISSN', [''])[0] if data.get('ISSN') else '',
            'authors': [],
            'year': '',
            'month': '',
            'volume': data.get('volume', ''),
            'issue': data.get('issue', ''),
            'page': data.get('page', ''),
            'type': data.get('type', ''),
            'indexing': '',
            'journal_scope': 'International',  # Most DOI-registered journals are international
        }
        
        # Extract publication date
        if 'published-print' in data:
            date_parts = data['published-print'].get('date-parts', [[]])[0]
        elif 'published-online' in data:
            date_parts = data['published-online'].get('date-parts', [[]])[0]
        else:
            date_parts = []
        
        if date_parts:
            if len(date_parts) >= 1:
                paper_data['year'] = str(date_parts[0])
            if len(date_parts) >= 2:
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                paper_data['month'] = month_names[date_parts[1] - 1] if date_parts[1] <= 12 else ''
        
        # Format month_year
        if paper_data['month'] and paper_data['year']:
            paper_data['month_year'] = f"{paper_data['month']} {paper_data['year']}"
        elif paper_data['year']:
            paper_data['month_year'] = paper_data['year']
        else:
            paper_data['month_year'] = ''
        
        # Extract authors with position information
        author_list = []
        corresponding_author_idx = -1
        
        if 'author' in data:
            for idx, author in enumerate(data['author']):
                given = author.get('given', '')
                family = author.get('family', '')
                full_name = f"{given} {family}".strip()
                
                if full_name:
                    author_info = {
                        'name': full_name,
                        'sequence': author.get('sequence', 'additional'),  # 'first' or 'additional'
                        'is_corresponding': False
                    }
                    
                    # Check for corresponding author indicators
                    # Some CrossRef records have affiliation or specific markers
                    if 'affiliation' in author:
                        for affil in author['affiliation']:
                            affil_name = affil.get('name', '').lower()
                            if 'corresponding' in affil_name or 'contact' in affil_name:
                                author_info['is_corresponding'] = True
                                corresponding_author_idx = idx
                    
                    author_list.append(author_info)
                    paper_data['authors'].append(full_name)
        
        # Determine author position for the first listed author
        paper_data['author_position'] = 'First Author'  # Default
        
        if author_list:
            first_author_info = author_list[0]
            
            # Check if first author is also corresponding author
            if first_author_info.get('is_corresponding'):
                paper_data['author_position'] = 'Corresponding Author'
            elif first_author_info.get('sequence') == 'first':
                paper_data['author_position'] = 'First Author'
            else:
                paper_data['author_position'] = 'Co-Author'
        
        # Format author names
        if paper_data['authors']:
            paper_data['author_name'] = paper_data['authors'][0]  # First author
            if len(paper_data['authors']) > 1:
                paper_data['collaborative_authors'] = ', '.join(paper_data['authors'][1:])
            else:
                paper_data['collaborative_authors'] = ''
            
            # Add all authors list for reference
            paper_data['all_authors'] = paper_data['authors']
            paper_data['total_authors'] = len(paper_data['authors'])
        
        # Format vol/issue/page
        vol_issue_page_parts = []
        if paper_data['volume']:
            vol_issue_page_parts.append(f"Vol.{paper_data['volume']}")
        if paper_data['issue']:
            vol_issue_page_parts.append(f"Issue.{paper_data['issue']}")
        if paper_data['page']:
            vol_issue_page_parts.append(f"pp.{paper_data['page']}")
        paper_data['vol_issue_page'] = ', '.join(vol_issue_page_parts)
        
        # Intelligent indexing detection based on publisher and journal metadata
        publisher_lower = paper_data['publisher'].lower()
        journal_lower = paper_data['journal_name'].lower()
        
        # Major publishers typically indexed in Scopus and Web of Science
        scopus_wos_publishers = [
            'springer', 'elsevier', 'wiley', 'ieee', 'nature', 'oxford', 
            'cambridge', 'taylor', 'sage', 'emerald', 'frontiers',
            'mdpi', 'hindawi', 'plos', 'bmc', 'acm', 'aaas'
        ]
        
        # SCI/SCIE/SSCI indicators (high-impact publishers)
        sci_publishers = [
            'nature', 'science', 'cell', 'lancet', 'nejm', 'jama',
            'springer', 'elsevier', 'wiley', 'oxford', 'cambridge'
        ]
        
        # Check publisher reputation
        is_major_publisher = any(pub in publisher_lower for pub in scopus_wos_publishers)
        is_high_impact = any(pub in publisher_lower for pub in sci_publishers)
        
        # Detect likely indexing (prioritize in order: WoS > Scopus > SCI)
        if is_high_impact:
            # High-impact publishers are often in WoS and SCI
            if 'nature' in publisher_lower or 'science' in journal_lower:
                paper_data['indexing'] = 'SCI/SCIE/SSCI'
            elif any(pub in publisher_lower for pub in ['ieee', 'acm', 'springer']):
                paper_data['indexing'] = 'WoS'
            else:
                paper_data['indexing'] = 'Scopus'
        elif is_major_publisher:
            paper_data['indexing'] = 'Scopus'
        else:
            paper_data['indexing'] = ''  # Unknown, user should verify
        
        # Add indexing confidence note
        if paper_data['indexing']:
            paper_data['indexing_note'] = f"Likely indexed (based on publisher: {paper_data['publisher']}). Please verify."
        else:
            paper_data['indexing_note'] = 'Indexing unclear. Please verify manually.'
        
        return jsonify(paper_data)
        
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timeout. Please try again.'}), 408
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error fetching DOI data: {str(e)}'}), 500

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

            request.form.get('publication_type', 'Journal'),
            request.form.get('status', 'Published'),

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
                publication_type, status,
                proof_filename
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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

# ---------------- EXCEL DASHBOARD ----------------
@app.route('/excel_dashboard')
@login_required
def excel_dashboard():
    conn = get_db_connection()
    
    # Get filter parameters
    dept_filter = request.args.get('dept', '')
    type_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '')
    author_filter = request.args.get('author', '')
    title_filter = request.args.get('title', '')
    publisher_filter = request.args.get('publisher', '')
    journal_filter = request.args.get('journal_name', '')
    scope_filter = request.args.get('scope', '')
    issn_filter = request.args.get('issn', '')
    scopus_filter = request.args.get('scopus', '')
    sci_filter = request.args.get('sci', '')
    wos_filter = request.args.get('wos', '')
    year_filter = request.args.get('year', '')
    collab_author_filter = request.args.get('collab_author', '')
    journal_status_filter = request.args.get('journal_status', '')
    
    query = 'SELECT * FROM journals WHERE 1=1'
    params = []
    
    if dept_filter:
        query += ' AND department = ?'
        params.append(dept_filter)
    if type_filter:
        query += ' AND publication_type = ?'
        params.append(type_filter)
    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)
    if author_filter:
        query += ' AND author_name LIKE ?'
        params.append(f'%{author_filter}%')
    if title_filter:
        query += ' AND paper_title LIKE ?'
        params.append(f'%{title_filter}%')
    if publisher_filter:
        query += ' AND publisher LIKE ?'
        params.append(f'%{publisher_filter}%')
    if journal_filter:
        query += ' AND journal_name LIKE ?'
        params.append(f'%{journal_filter}%')
    if scope_filter:
        query += ' AND journal_scope = ?'
        params.append(scope_filter)
    if issn_filter:
        query += ' AND issn_number LIKE ?'
        params.append(f'%{issn_filter}%')
    if scopus_filter:
        query += ' AND is_scopus = ?'
        params.append(int(scopus_filter))
    if sci_filter:
        query += ' AND is_sci_scie_ssci = ?'
        params.append(int(sci_filter))
    if wos_filter:
        query += ' AND is_wos = ?'
        params.append(int(wos_filter))
    if year_filter:
        query += ' AND (publication_year = ? OR month_year LIKE ?)'
        params.append(year_filter)
        params.append(f'%{year_filter}%')
    if collab_author_filter:
        query += ' AND collaborative_authors LIKE ?'
        params.append(f'%{collab_author_filter}%')
    if journal_status_filter:
        query += ' AND journal_status = ?'
        params.append(journal_status_filter)
        
    query += ' ORDER BY department ASC, paper_title ASC'
    journals = conn.execute(query, params).fetchall()
    
    # Summary statistics based on filtered results
    stats = {
        'total': len(journals),
        'journals': len([j for j in journals if j['publication_type'] == 'Journal']),
        'papers': len([j for j in journals if j['publication_type'] == 'Paper']),
        'books': len([j for j in journals if j['publication_type'] == 'Book']),
        'published': len([j for j in journals if j['status'] == 'Published']),
        'accepted': len([j for j in journals if j['status'] == 'Accepted']),
        'submitted': len([j for j in journals if j['status'] == 'Submitted']),
        'rejected': len([j for j in journals if j['status'] == 'Rejected']),
        'working': len([j for j in journals if j['status'] == 'Working Process'])
    }

    # Department-wise statistics
    unique_depts = sorted(list(set([j['department'] for j in journals if j['department']])))
    dept_stats = {d: len([j for j in journals if j['department'] == d]) for d in unique_depts}
    
    # Get unique departments for filter dropdown (sorted A-Z)
    depts = conn.execute("SELECT DISTINCT department FROM journals WHERE department IS NOT NULL AND department != '' ORDER BY department ASC").fetchall()
    
    conn.close()
    
    return render_template('excel_dashboard.html', 
                          journals=journals, 
                          stats=stats, 
                          depts=depts,
                          dept_stats=dept_stats,
                          current_filters={
                              'dept': dept_filter, 'type': type_filter, 'status': status_filter,
                              'author': author_filter, 'title': title_filter,
                              'publisher': publisher_filter, 'journal_name': journal_filter,
                              'scope': scope_filter, 'issn': issn_filter,
                              'scopus': scopus_filter, 'sci': sci_filter, 'wos': wos_filter,
                              'year': year_filter, 'collab_author': collab_author_filter,
                              'journal_status': journal_status_filter
                          })

@app.route('/upload_excel', methods=['POST'])
@login_required
def upload_excel():
    if 'excel_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['excel_file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
        
    if file and file.filename.endswith(('.xlsx', '.xls')):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Read first 10 rows to find header row if not first
            temp_df = pd.read_excel(file_path, nrows=10, header=None)
            header_row = 0
            found_header = False
            
            # Simple heuristic: row with most matches for common keywords is likely the header
            keywords_to_find = ['title', 'journal', 'author', 'dept', 'issn', 'scopus']
            max_matches = 0
            
            for idx, row in temp_df.iterrows():
                matches = sum(1 for cell in row if any(kw in str(cell).lower() for kw in keywords_to_find))
                if matches > max_matches:
                    max_matches = matches
                    header_row = idx
                    found_header = True if matches >= 2 else False

            # Read again with detected header row
            df = pd.read_excel(file_path, header=header_row)
            if df.empty:
                return jsonify({'success': False, 'error': 'The Excel file is empty'}), 400
            
            # Normalize column names: trim and lowercase
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            conn = get_db_connection()
            count = 0
            for _, row in df.iterrows():
                # IMPROVED FUZZY MATCHER WITH NORMALIZATION
                def get_val(df_row, primary_headers, keywords=None, default=None):
                    # 1. Try exact/primary matches
                    for h in primary_headers:
                        h_norm = str(h).strip().lower()
                        if h_norm in df_row.index:
                            val = df_row[h_norm]
                            if not pd.isna(val) and val is not None:
                                return str(val).strip() if isinstance(val, str) else val
                    
                    # 2. Try fuzzy keyword matches if enabled
                    if keywords:
                        for col in df_row.index:
                            for kw in keywords:
                                if str(kw).lower() in str(col).lower():
                                    val = df_row[col]
                                    if not pd.isna(val) and val is not None:
                                        return str(val).strip() if isinstance(val, str) else val
                    
                    return default

                def normalize_bool(val):
                    if val is None or pd.isna(val): return 0
                    s = str(val).strip().lower()
                    if s in ['1', '1.0', 'yes', 'y', '✓', 'true', 'scopus', 'sci', 'wos']: return 1
                    return 0

                def to_float(val):
                    if val is None or pd.isna(val): return None
                    try:
                        return float(str(val).strip())
                    except (ValueError, TypeError):
                        return None

                data = (
                    get_val(row, ['Journal Status'], ['status'], 'Published'),
                    get_val(row, ['Department', 'Department Name', 'Dept', 'Branch', 'Dept.'], ['dept', 'department', 'branch']),
                    get_val(row, ['Author Position', 'Author Prefix'], ['position', 'prefix']),
                    get_val(row, ['Author Name'], ['author', 'name', 'faculty']),
                    get_val(row, ['Collaborative Authors'], ['collaborator', 'co-author'], ''),
                    get_val(row, ['Paper Title', 'Title of Paper', 'Title of the Paper', 'Title'], ['title', 'research', 'article', 'topic', 'name', 'paper', 'article', 'top']),
                    get_val(row, ['Publisher'], ['publisher', 'press'], ''),
                    get_val(row, ['Journal Name', 'Name of the Journal'], ['journal', 'publication'], ''),
                    get_val(row, ['Journal Scope', 'International/National'], ['scope', 'field', 'international', 'national'], ''),
                    get_val(row, ['Vol/Issue/Page', 'Volume'], ['volume', 'issue', 'page'], ''),
                    get_val(row, ['Month/Year', 'Month'], ['month'], ''),
                    get_val(row, ['ISSN', 'ISSN Number'], ['issn'], ''),
                    normalize_bool(get_val(row, ['Scopus'], ['scopus'])),
                    normalize_bool(get_val(row, ['SCI', 'SCI/SCIE/SSCI'], ['sci', 'scie', 'ssci'])),
                    normalize_bool(get_val(row, ['WoS', 'Web of Science'], ['wos'])),
                    to_float(get_val(row, ['Impact Factor'], ['impact'])),
                    to_float(get_val(row, ['Citation Score', 'Citation'], ['citation'])),
                    get_val(row, ['SJR', 'SJR Rating'], ['sjr'], None),
                    to_float(get_val(row, ['h-index', 'H Index', 'h index'], ['h-index', 'hindex'])),
                    get_val(row, ['Anna Univ', 'Q1 to Q4', 'Q1-Q4', 'Quartile'], ['anna', 'quartile', 'q1'], None),
                    get_val(row, ['Preview', 'Plotview', 'Preview Link'], ['preview', 'plotview'], None),
                    get_val(row, ['Journal Metrics Page', 'Home Page', 'Home Page Link'], ['metrics', 'home page'], None),
                    get_val(row, ['DOI', 'DOI Link'], ['doi'], None),
                    get_val(row, ['Collab Scope', 'International/National Indexing', 'Collaboration Scope'], ['collab scope', 'indexing scope'], None),
                    get_val(row, ['Collab Institution', 'National Indexing', 'Agency', 'National/International Agency'], ['collab inst', 'agency'], None),
                    get_val(row, ['Publication Type'], ['type', 'category', 'kind'], 'Journal'),
                    get_val(row, ['Status', 'Publication Status', 'Working Status', 'Paper Status'], ['working', 'progress', 'status'], 'Published'),
                    get_val(row, ['Publication Year', 'Year'], ['year', 'pub year'], None),
                )
                
                # Check for essential data - more lenient: skip only if both title and journal name are missing
                if not data[5] and not data[7]: 
                    continue

                conn.execute("""
                    INSERT INTO journals (
                        journal_status, department, author_position, author_name, collaborative_authors,
                        paper_title, publisher, journal_name, journal_scope, vol_issue_page,
                        month_year, issn_number, is_scopus, is_sci_scie_ssci, is_wos,
                        impact_factor, citation_score, sjr_rating, h_index, anna_univ_list,
                        preview_link, home_page_link, doi_link,
                        collab_scope, collab_institution,
                        publication_type, status, publication_year
                    )
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, data)
                count += 1
            
            conn.commit()
            conn.close()
            
            if count == 0:
                cols_str = ", ".join(df.columns[:10]) # Show first 10 columns for debugging
                return jsonify({'success': False, 'error': f'No valid data rows found. Detected columns: {cols_str}. Make sure your Excel has a "Paper Title" or "Journal Name" column.'}), 400

            # Identify departments found for feedback
            dept_cols = [c for c in df.columns if any(kw in str(c).lower() for kw in ['dept', 'department', 'branch'])]
            depts_found = df[dept_cols[0]].dropna().unique().tolist() if not df.empty and dept_cols else []
            dept_msg = f" (Departments: {', '.join(map(str, depts_found))})" if depts_found else ""
            
            os.remove(file_path)
            return jsonify({'success': True, 'message': f'Successfully uploaded {count} records!{dept_msg}'})
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'success': False, 'error': f'Error processing Excel: {str(e)}'}), 500
    
    return jsonify({'success': False, 'error': 'Invalid file format. Please upload .xlsx or .xls'}), 400

@app.route('/delete_journal/<int:id>', methods=['POST'])
@login_required
def delete_journal(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM journals WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Record deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete_journals_batch', methods=['POST'])
@login_required
def delete_journals_batch():
    try:
        data = request.get_json()
        ids = data.get('ids', [])
        if not ids:
            return jsonify({'success': False, 'error': 'No records selected'}), 400
        
        conn = get_db_connection()
        # Use comma-separated list of IDs for a single DELETE query
        query = f"DELETE FROM journals WHERE id IN ({','.join(['?'] * len(ids))})"
        conn.execute(query, ids)
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Successfully deleted {len(ids)} records'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
