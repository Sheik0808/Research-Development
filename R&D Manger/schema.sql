-- User Table for Authentication
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('faculty', 'student', 'admin')),
    full_name TEXT NOT NULL,
    department TEXT,
    designation TEXT,
    credits INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rewards/Credits History Table
DROP TABLE IF EXISTS rewards;
CREATE TABLE rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    credits_earned INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sessions Table (optional but recommended)
DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Login Log Table (Track login times)
DROP TABLE IF EXISTS login_logs;
CREATE TABLE login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP,
    ip_address TEXT,
    device_info TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS journals;

CREATE TABLE journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Basic Details
    journal_status TEXT,
    department TEXT,
    author_position TEXT,
    author_name TEXT,
    collaborative_authors TEXT,

    -- Paper Details
    paper_title TEXT,
    publisher TEXT,
    journal_name TEXT,
    journal_scope TEXT,
    vol_issue_page TEXT,
    month_year TEXT,
    publication_year INTEGER,
    issn_number TEXT,
    publication_type TEXT DEFAULT 'Journal', -- ✅ CATEGORY: Journal, Paper, Book
    status TEXT DEFAULT 'Published',         -- ✅ STATUS: Published, Submitted, Working Process

    -- Indexing & Metrics
    is_scopus INTEGER DEFAULT 0,
    is_sci_scie_ssci INTEGER DEFAULT 0,
    is_wos INTEGER DEFAULT 0,
    impact_factor REAL,
    citation_score REAL,
    sjr_rating TEXT,
    h_index REAL,
    anna_univ_list TEXT,

    -- Links
    preview_link TEXT,
    home_page_link TEXT,
    doi_link TEXT,

    -- Collaboration Details
    collab_scope TEXT,
    collab_institution TEXT,

    proof_filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
