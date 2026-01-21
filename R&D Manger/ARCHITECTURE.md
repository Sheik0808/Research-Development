# System Architecture - Authentication Flow

## 🏗️ Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      KITE R&D Portal                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Login Page   │  │ Signup Page  │  │ Authenticated Routes │  │
│  │              │  │              │  │                      │  │
│  │ - Username   │  │ - Role Select│  │ - Dashboard          │  │
│  │ - Password   │  │ - Full Name  │  │ - Add Journal        │  │
│  │              │  │ - Username   │  │ - View Journals      │  │
│  └──────┬───────┘  │ - Email      │  │ - Logout             │  │
│         │          │ - Department │  └──────────┬───────────┘  │
│         │          │ - Password   │             │              │
│         │          └──────┬───────┘             │              │
│         │                 │                     │              │
│         └─────────────────┼─────────────────────┘              │
│                           │                                    │
│                    [Login Required Decorator]                 │
│                           │                                    │
│         ┌─────────────────▼──────────────────┐               │
│         │    Session Management              │               │
│         │  ┌────────────────────────────┐   │               │
│         │  │ user_id                    │   │               │
│         │  │ username                   │   │               │
│         │  │ role (faculty/student)     │   │               │
│         │  │ full_name                  │   │               │
│         │  └────────────────────────────┘   │               │
│         └──────────────────────────────────┘               │
│                           │                                    │
│         ┌─────────────────▼──────────────────┐               │
│         │    SQLite Database                  │               │
│         │  ┌──────────────────────────────┐  │               │
│         │  │ users                        │  │               │
│         │  │ - id, username, email, pwd   │  │               │
│         │  │ - role, full_name, dept      │  │               │
│         │  │                              │  │               │
│         │  │ journals (existing)          │  │               │
│         │  │ - all publication data       │  │               │
│         │  └──────────────────────────────┘  │               │
│         └──────────────────────────────────┘               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Authentication Flow Diagram

```
┌─────────────┐
│  User Visit │
│   http://:  │
│   5000      │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│ Check Session        │
│ (user_id exists?)    │
└──────┬────────┬──────┘
       │        │
   YES│        │NO
       │        │
       │   ┌────▼────────────────┐
       │   │ Redirect to /login  │
       │   └────┬────────────────┘
       │        │
       │   ┌────▼─────────────────────┐
       │   │ Login Page Displayed      │
       │   │ or Signup Page if new     │
       │   └────┬─────────────────────┘
       │        │
       │   ┌────▼──────────────────────────┐
       │   │ User Enters Credentials       │
       │   │ (username/password)           │
       │   └────┬───────────────────────────┘
       │        │
       │   ┌────▼──────────────────────────┐
       │   │ Query Database for User       │
       │   │ Check Username Exists         │
       │   └────┬──────┬──────────────────┘
       │        │      │
       │   FOUND│  NOT │
       │        │   FOUND
       │        │      │
       │        │  ┌───▼────────────┐
       │        │  │ Error: User not│
       │        │  │ found          │
       │        │  └───┬────────────┘
       │        │      │
       │   ┌────▼──────┴─────────────────┐
       │   │ Show Error & Retry          │
       │   └─────────────────────────────┘
       │
       │   ┌────────────────────────────────┐
       │   │ Verify Password Hash           │
       │   │ (check_password_hash)          │
       │   └────┬────┬─────────────────────┘
       │        │    │
       │      VALID  │INVALID
       │        │    │
       │        │  ┌─▼──────────────────┐
       │        │  │ Error: Wrong pwd   │
       │        │  │ Show on login page │
       │        │  └─┬──────────────────┘
       │        │    │
       │        │  ┌─▼────────────────────┐
       │        │  │ Retry login          │
       │        │  └──────────────────────┘
       │        │
       │   ┌────▼──────────────────────────┐
       │   │ Create Session                 │
       │   │ - user_id                      │
       │   │ - username                     │
       │   │ - role                         │
       │   │ - full_name                    │
       │   └────┬───────────────────────────┘
       │        │
       │   ┌────▼──────────────────────────┐
       │   │ Redirect to Dashboard          │
       │   └────┬───────────────────────────┘
       │        │
       ▼        ▼
┌──────────────────────────────┐
│   Dashboard Displayed        │
│ ✓ User info shown in navbar  │
│ ✓ Stats & metrics loaded     │
│ ✓ Can add/view publications  │
└──────────────────────────────┘
```

---

## 📊 Database Schema Diagram

```
┌─────────────────────────────────────────────────────┐
│                   DATABASE.DB                        │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │ users Table                                   │   │
│  ├──────────────────────────────────────────────┤   │
│  │ id (PK)          │ INTEGER PRIMARY KEY       │   │
│  │ username (UQ)    │ TEXT UNIQUE NOT NULL      │   │
│  │ email (UQ)       │ TEXT UNIQUE NOT NULL      │   │
│  │ password         │ TEXT NOT NULL (HASHED)    │   │
│  │ role             │ TEXT (faculty/student)    │   │
│  │ full_name        │ TEXT NOT NULL             │   │
│  │ department       │ TEXT                      │   │
│  │ designation      │ TEXT                      │   │
│  │ created_at       │ TIMESTAMP                 │   │
│  └──────────────────────────────────────────────┘   │
│                          │                          │
│                          │ (FK)                     │
│                          │                          │
│  ┌──────────────────────┴────────────────────────┐  │
│  │ sessions Table (Optional)                      │  │
│  ├─────────────────────────────────────────────┤  │
│  │ id (PK)          │ INTEGER PRIMARY KEY       │  │
│  │ user_id (FK)     │ INTEGER NOT NULL          │  │
│  │ session_token    │ TEXT UNIQUE NOT NULL      │  │
│  │ created_at       │ TIMESTAMP                 │  │
│  │ expires_at       │ TIMESTAMP                 │  │
│  └──────────────────────────────────────────────┘  │
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │ journals Table (Existing - Unchanged)         │   │
│  ├──────────────────────────────────────────────┤   │
│  │ id, journal_status, department, author_*     │   │
│  │ paper_title, publisher, journal_name, etc.   │   │
│  │ (All existing fields preserved)               │   │
│  └──────────────────────────────────────────────┘   │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## 🗺️ Application Routes Map

```
HTTP://127.0.0.1:5000
│
├─ GET /login ──────────────► Show Login Form
│
├─ POST /login ──────────────► Validate & Create Session
│                                    │
│                                    ├─ Invalid ──► Show Error
│                                    └─ Valid ────► Redirect to /
│
├─ GET /signup ─────────────► Show Signup Form
│
├─ POST /signup ────────────► Create User Account
│                                    │
│                                    ├─ Invalid ──► Show Error
│                                    └─ Valid ────► Redirect to /login
│
├─ GET / (Protected) ────────► Show Dashboard
│
├─ GET /add_journal (Protected) ──► Show Form
│ └─ POST /add_journal ───────────► Save Journal
│
├─ GET /view_journals (Protected) ─► List All Journals
│
└─ GET /logout ─────────────► Clear Session → Redirect to /login
```

---

## 👤 User Role Hierarchy

```
┌──────────────────────────────────────┐
│      Unauthenticated User            │
│  (Can only access /login, /signup)   │
└────────────┬─────────────────────────┘
             │
             │ (Login/Signup)
             │
             ▼
┌──────────────────────────────────────┐
│       Authenticated User              │
│   (Can access all protected routes)   │
├──────────────────────────────────────┤
│                                        │
│  ┌──────────────┐  ┌──────────────┐  │
│  │   FACULTY    │  │   STUDENT    │  │
│  ├──────────────┤  ├──────────────┤  │
│  │ • Add Journal│  │ • Add Journal│  │
│  │ • View       │  │ • View       │  │
│  │   Journals   │  │   Journals   │  │
│  │ • Dashboard  │  │ • Dashboard  │  │
│  │              │  │              │  │
│  │ *Future:     │  │ *Future:     │  │
│  │  - Approval  │  │  - Limited   │  │
│  │  - Reports   │  │    Edit      │  │
│  │  - Admin     │  │  - Viewing   │  │
│  └──────────────┘  └──────────────┘  │
│                                        │
└──────────────────────────────────────┘
```

---

## 🔐 Password Security Flow

```
Signup Process:
┌──────────────────┐
│ User enters pwd  │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Password Validation                      │
│ - Minimum 8 characters                   │
│ - Confirm password matches                │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Generate Password Hash                   │
│ Using: werkzeug.security.                │
│        generate_password_hash()          │
│ Result: salted + hashed password        │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Store in Database                        │
│ users.password = hashed_value           │
│ (Original password never stored)         │
└────────┬────────────────────────────────┘
         │
         ▼
    [DONE - Secure]


Login Process:
┌──────────────────┐
│ User enters pwd  │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Fetch user from database                 │
│ Get: users.password (hashed value)      │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Verify Password Hash                     │
│ Using: werkzeug.security.                │
│        check_password_hash()             │
│ Compare: input pwd vs stored hash       │
└────────┬────────────────────────────────┘
         │
    ┌────┴──────┐
    │            │
   Match       No Match
    │            │
    ▼            ▼
  Valid       Invalid
    │            │
    ▼            ▼
[ALLOW]    [REJECT - Error]
```

---

## 📱 User Interface Structure

```
┌────────────────────────────────────────────────────────────┐
│ KITE R&D Portal                          👤User ▼  [Logout]│
├────────────────────────────────────────────────────────────┤
│                                                              │
│ [+ Add Publication] [👁️View Reports]                      │
│                                                              │
├────────────────────────────────────────────────────────────┤
│                                                              │
│                      DASHBOARD CONTENT                      │
│                      (After Login)                          │
│                                                              │
│    ┌──────────────┐  ┌────────────────┐                   │
│    │ Total        │  │ Department     │                   │
│    │ Journals: 42 │  │ Stats: ...     │                   │
│    └──────────────┘  └────────────────┘                   │
│                                                              │
│    ┌──────────────┐  ┌────────────────┐                   │
│    │ Faculty      │  │ Indexing       │                   │
│    │ Stats: ...   │  │ Metrics: ...   │                   │
│    └──────────────┘  └────────────────┘                   │
│                                                              │
├────────────────────────────────────────────────────────────┤
│ © 2025 KITE R&D Management System                          │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 Session Lifecycle

```
Timeline:
─────────────────────────────────────────────────────────

1. User Visits
   └─► No session cookie exists

2. User Logs In
   └─► create_session()
       ├─ user_id = 5
       ├─ username = "john_smith"
       ├─ role = "faculty"
       └─ full_name = "Dr. John Smith"

3. Session Active
   └─► Can access protected routes
       ├─ Dashboard accessible
       ├─ Add Journal accessible
       ├─ View Journals accessible
       └─ All routes allowed

4. User Performs Actions
   ├─► Each request includes session
   ├─► System validates session
   └─► Routes accessible

5. User Clicks Logout
   ├─► session.clear()
   ├─► All session data removed
   └─► Redirect to login

6. Session Expires
   └─► No active session
       └─► Redirect to login on next request
```

---

## 📊 File Structure with New Files

```
R&D Manger/
│
├── 📄 app.py ⭐ (MODIFIED)
│   ├── Authentication routes
│   ├── Session management
│   └── Login decorator
│
├── 📄 schema.sql ⭐ (MODIFIED)
│   ├── users table (NEW)
│   ├── sessions table (NEW)
│   └── journals table (existing)
│
├── 📁 templates/
│   ├── 🆕 login.html (NEW)
│   ├── 🆕 signup.html (NEW)
│   ├── ⭐ base.html (MODIFIED - added user dropdown)
│   ├── dashboard.html
│   ├── add_journal.html
│   └── view_journals.html
│
├── 📁 static/
│   ├── style.css
│   └── calendar.js
│
├── 📁 uploads/
│   └── [uploaded files]
│
├── 📚 Documentation (NEW)
│   ├── 🆕 AUTHENTICATION_GUIDE.md
│   ├── 🆕 QUICK_START.md
│   ├── 🆕 IMPLEMENTATION_SUMMARY.md
│   └── 🆕 ARCHITECTURE.md (this file)
│
└── 📄 database.db
    └── (Created on first run)
```

---

**Status**: ✅ Complete Architecture  
**Version**: 1.0  
**Date**: January 2026
