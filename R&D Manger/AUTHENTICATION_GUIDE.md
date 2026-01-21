# KITE R&D Management System - Authentication Guide

## Overview
The R&D Management System now includes a complete authentication system with role-based access (Faculty & Student).

## Features Implemented

### 1. **User Authentication**
- Secure login/signup system
- Password hashing using Werkzeug security
- Session-based authentication
- Role-based access control (Faculty & Student)

### 2. **User Roles**
- **Faculty**: Can manage research publications and reports
- **Student**: Can view and contribute to R&D publications

### 3. **Database Schema**
Two new tables have been added:

#### `users` table
```sql
- id: Unique user identifier
- username: Unique username
- email: Unique email address
- password: Hashed password
- role: User role (faculty/student)
- full_name: User's full name
- department: User's department
- designation: Job title or year/semester
- created_at: Account creation timestamp
```

#### `sessions` table (Optional - for advanced session tracking)
```sql
- id: Session identifier
- user_id: Reference to user
- session_token: Unique session token
- created_at: Session creation time
- expires_at: Session expiration time
```

## Pages and Routes

### Public Routes (No Login Required)
- **`/login`** - User login page
- **`/signup`** - User registration page

### Protected Routes (Login Required)
- **`/`** - Dashboard (displays stats and metrics)
- **`/add_journal`** - Add new publication
- **`/view_journals`** - View all publications
- **`/logout`** - End user session

## Usage Instructions

### First Time Setup
1. Start the application:
   ```bash
   python app.py
   ```

2. Access the application at `http://127.0.0.1:5000`

3. You'll be redirected to the login page if not authenticated

### Creating an Account (Sign Up)

1. Click "Sign Up Here" on the login page
2. Fill in the registration form:
   - **Select Role**: Choose between Faculty or Student
   - **Full Name**: Enter your full name
   - **Username**: Choose a unique username
   - **Email**: Enter a valid email address
   - **Department**: Your department/faculty
   - **Designation**: Your position or academic year
   - **Password**: Create a secure password (min. 8 characters)
   - **Confirm Password**: Re-enter password to confirm

3. Click "Create Account"

4. You'll be redirected to login - enter your credentials

### Logging In

1. Enter your username
2. Enter your password
3. Click "Sign In"
4. You'll be taken to the dashboard

### User Profile Display

Once logged in, the navbar shows:
- User's first name (abbreviated)
- A dropdown menu with:
  - Full name
  - User role badge (FACULTY/STUDENT)
  - Logout option

### Security Features

- **Password Hashing**: All passwords are hashed using werkzeug.security
- **Session Management**: User sessions are maintained via Flask sessions
- **Login Decorator**: Protected routes use `@login_required` decorator
- **Error Handling**: Clear error messages for validation failures
- **Input Validation**: Form validation on both client and server side

## File Structure

```
R&D Manger/
├── app.py                    # Main Flask application (UPDATED)
├── schema.sql               # Database schema (UPDATED)
├── templates/
│   ├── login.html          # Login page (NEW)
│   ├── signup.html         # Registration page (NEW)
│   ├── base.html           # Base template (UPDATED)
│   ├── dashboard.html      # Dashboard
│   ├── add_journal.html    # Add publication
│   └── view_journals.html  # View publications
├── static/
│   ├── style.css          # Stylesheets
│   └── calendar.js        # Calendar functionality
└── uploads/               # File upload folder
```

## Technical Implementation

### Authentication Flow

```
User Request
    ↓
Check Session Cookie
    ↓
Session Valid? → YES → Continue to Route
    ↓
    NO
    ↓
Redirect to /login
    ↓
User Enters Credentials
    ↓
Verify Username & Password
    ↓
Valid? → YES → Create Session → Redirect to Dashboard
    ↓
    NO
    ↓
Show Error & Redirect to /login
```

### Password Security
- Uses `werkzeug.security.generate_password_hash()` for hashing
- Uses `werkzeug.security.check_password_hash()` for verification
- Passwords are never stored in plain text

### Session Management
- Sessions are stored in Flask's session cookies
- Contains: user_id, username, role, full_name
- Automatically cleared on logout
- Can be configured to expire after inactivity

## Customization Options

### Modify Password Requirements
Edit in `signup()` function in `app.py`:
```python
minlength="8"  # Change minimum password length
```

### Add Additional User Fields
1. Add new columns to `users` table in `schema.sql`
2. Update signup form in `templates/signup.html`
3. Update signup route in `app.py`

### Add Role-Specific Permissions
```python
from functools import wraps

def faculty_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'faculty':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
```

## Testing the System

### Test Account Credentials
You can create test accounts with:
- **Faculty Account**:
  - Username: `prof_john`
  - Email: `john@kite.edu`
  - Role: Faculty

- **Student Account**:
  - Username: `student_alex`
  - Email: `alex@kite.edu`
  - Role: Student

## Security Best Practices

1. **Change Secret Key**: Update `app.secret_key` in production
   ```python
   app.secret_key = 'generate-a-strong-random-secret-key'
   ```

2. **Use HTTPS**: In production, enable HTTPS to encrypt sessions

3. **Database Backups**: Regularly backup the database.db file

4. **Email Verification**: Consider adding email verification for sign-ups

5. **Rate Limiting**: Add login attempt rate limiting to prevent brute force

## Troubleshooting

### Issue: "Incorrect username" when logging in
- **Solution**: Ensure username is spelled correctly and account exists

### Issue: "Passwords do not match" on signup
- **Solution**: Confirm both password fields contain identical text

### Issue: "Username already exists"
- **Solution**: Choose a different username - the one entered is taken

### Issue: Session expires immediately
- **Solution**: Clear browser cookies and login again, or check if session secret key has changed

## Future Enhancements

- [ ] Email verification for new accounts
- [ ] Password reset functionality
- [ ] Two-factor authentication
- [ ] User profile management
- [ ] Admin dashboard
- [ ] Role-based view permissions
- [ ] Activity logs and audit trails
- [ ] API authentication with tokens

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Developed For**: KITE R&D Management System
