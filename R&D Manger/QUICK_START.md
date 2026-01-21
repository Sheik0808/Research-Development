# Quick Start Guide - Authentication System

## What's New?

✅ **Login System** - Secure user authentication  
✅ **Sign Up** - Register as Faculty or Student  
✅ **User Dashboard** - Personalized greeting with user info  
✅ **Session Management** - Automatic login/logout  
✅ **Protected Routes** - Publications require authentication

---

## Access Your Application

### Step 1: Start the Server
```bash
cd "R&D Manger"
python app.py
```

### Step 2: Open Browser
Navigate to: **http://127.0.0.1:5000**

### Step 3: You'll See the Login Page
```
┌─────────────────────────────┐
│   🧪 KITE R&D Portal       │
│   Research & Development   │
│                             │
│  Username: [____________]  │
│  Password: [____________]  │
│                             │
│    [Sign In]                │
│                             │
│  New User? Sign Up Here    │
└─────────────────────────────┘
```

---

## Creating Your First Account

### For Faculty

1. Click **"Sign Up Here"**
2. Select **Faculty** (click the card)
3. Fill in:
   - Full Name: `Dr. John Smith`
   - Username: `john_smith`
   - Email: `john@kite.edu`
   - Department: `Computer Science`
   - Designation: `Associate Professor`
   - Password: `SecurePass123`
4. Click **"Create Account"**
5. Login with your new credentials

### For Student

1. Click **"Sign Up Here"**
2. Select **Student** (click the card)
3. Fill in:
   - Full Name: `Alex Johnson`
   - Username: `alex_johnson`
   - Email: `alex@kite.edu`
   - Department: `Computer Science`
   - Designation: `2nd Year`
   - Password: `StudentPass123`
4. Click **"Create Account"**
5. Login with your new credentials

---

## Using the Dashboard

### After Login
```
Navbar: 🧪 KITE R&D Portal  [+Add Publication]  [👁️View Reports]  [👤Alex J ▼]
```

### User Menu Dropdown
Click your name to see:
- Full Name
- Role Badge (FACULTY / STUDENT)
- Logout option

### Main Functions
| Button | Function |
|--------|----------|
| **Add Publication** | Create new journal entry |
| **View Reports** | See all publications |
| **User Profile** | Logout or view info |

---

## Authentication Flow

### Login Process
```
1. Enter Username & Password
   ↓
2. System verifies credentials
   ↓
3. If valid → Create session → Go to Dashboard
   ↓
   If invalid → Show error → Redirect to Login
```

### Protected Pages
- Dashboard (/)
- Add Journal (/add_journal)
- View Journals (/view_journals)

**Note:** These pages will redirect to login if not authenticated!

---

## Database Changes

### New Tables Created

#### Users Table
```
id          → Unique ID
username    → Login username (unique)
email       → Email address (unique)
password    → Hashed password
role        → "faculty" or "student"
full_name   → User's name
department  → Department name
designation → Position/Year
created_at  → Registration date
```

---

## Security Features

🔐 **Password Hashing** - Passwords are encrypted  
🔐 **Session Security** - Automatic session management  
🔐 **Input Validation** - Server-side form validation  
🔐 **Protected Routes** - Unauthorized access prevented  

---

## Common Actions

### Logout
1. Click on your name in the top-right
2. Click "Logout"
3. You'll return to login page

### Change Account
1. Logout
2. Click "Sign In Here"
3. Enter different credentials

### Forgotten Password
- Currently: Create a new account
- Future: Password reset feature

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Login failed | Check username/password spelling |
| Account exists | Username taken, choose different one |
| Passwords don't match | Ensure both passwords are identical |
| Can't access dashboard | Must be logged in first |
| Session expired | Login again |

---

## Role Differences

### Faculty Access
- ✓ Add publications
- ✓ View all reports
- ✓ Manage own entries

### Student Access
- ✓ Add publications
- ✓ View all reports
- ✓ Contribute to projects

*Note: Both roles have same access to publications. Role differences can be added in the future.*

---

## Testing Accounts

Try these test credentials after signing up:

**Test Faculty**
```
Username: test_faculty
Email: faculty@kite.edu
Role: Faculty
```

**Test Student**
```
Username: test_student
Email: student@kite.edu
Role: Student
```

---

## Next Steps

1. ✅ Start the server
2. ✅ Create a test account
3. ✅ Login and explore
4. ✅ Add a publication
5. ✅ View all publications
6. ✅ Try logging out and back in

---

**Need Help?** Check `AUTHENTICATION_GUIDE.md` for detailed documentation.
