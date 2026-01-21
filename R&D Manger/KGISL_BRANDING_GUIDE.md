# KGISL Logo & Branding Guide

## About KGISL Branding

This R&D Management Portal has been configured to display the KGISL Institute of Technology logo and branding throughout the application.

## Adding Your KGISL Logo

### Step 1: Prepare Your Logo Files

You need to place your official KGISL Institute of Technology logo files in the following directory:

```
static/images/
```

### Step 2: Logo File Options

The application looks for the logo at:
- **Recommended:** `static/images/kgisl_logo.png` (PNG format)
- **Alternative:** `static/images/kgisl_logo.svg` (SVG format - scalable)

**A placeholder SVG logo has been created at:** `static/images/kgisl_logo.svg`

### Step 3: Supported Logo Formats

| Format | Location | Benefits |
|--------|----------|----------|
| PNG | `static/images/kgisl_logo.png` | Universal support, clear, professional |
| SVG | `static/images/kgisl_logo.svg` | Scalable, crisp on all devices |
| JPG | `static/images/kgisl_logo.jpg` | Widely supported |

### Step 4: Logo Requirements

- **Dimensions:** Preferably square or rectangular (recommended: 200x200px minimum)
- **Background:** Transparent background recommended for PNG/SVG
- **Color:** Should work well on gradient backgrounds (white/light colors work best)
- **Size:** Keep file size under 500KB for optimal performance

### Step 5: Integration Points

Your KGISL logo will appear in the following locations:

1. **Navigation Bar** - All authenticated pages (left side)
   - Height: 50px
   - Location: Next to "KGISL Institute of Technology / R&D Portal" text

2. **Login Page** - Visitor login screen
   - Height: 60px
   - Centered above login form

3. **Sign Up Page** - Registration form
   - Height: 60px
   - Centered above signup form

4. **Registration Success Page** - After successful account creation
   - Height: 70px
   - Prominent display with welcome message

5. **Admin Dashboard** - Can be added if needed
6. **Faculty Dashboard** - Can be added if needed
7. **Thank You Pages** - Can be added if needed

### Step 6: How to Add Your Logo

#### Option A: Direct File Placement

1. Save your KGISL logo as `kgisl_logo.png` (or .svg)
2. Place it in the `static/images/` directory
3. Restart the Flask server
4. The logo will automatically appear in all pages

#### Option B: Custom Logo Name

If you want to use a different filename:

1. Edit the template files:
   - `templates/base.html`
   - `templates/login.html`
   - `templates/signup.html`
   - `templates/registration_success.html`

2. Replace `kgisl_logo.png` with your preferred filename in all references

### Step 7: Testing

After adding your logo:

1. Navigate to `http://127.0.0.1:5000/login`
2. Verify the logo appears correctly on login page
3. Sign up and verify logo appears on all pages
4. Check that logo displays properly on different screen sizes
5. Test responsive design on mobile/tablet devices

### Step 8: Logo Styling Options

The logo styling can be customized in the templates:

```html
<!-- Current styling -->
<img src="{{ url_for('static', filename='images/kgisl_logo.png') }}" 
     alt="KGISL Logo" 
     style="height: 50px; margin-right: 12px; filter: brightness(1.1);"
     onerror="this.style.display='none'">
```

**Available CSS filters:**
- `brightness()` - Adjust brightness (0.5 = darker, 1.5 = brighter)
- `contrast()` - Adjust contrast
- `drop-shadow()` - Add shadow effect
- `filter: grayscale(0%)` - Full color (default)
- `filter: grayscale(100%)` - Grayscale (black & white)

### Step 9: Troubleshooting

**Logo not appearing?**
- Check file exists at: `static/images/kgisl_logo.png`
- Verify filename matches exactly (case-sensitive on Linux/Mac)
- Check file permissions (should be readable)
- Try clearing browser cache (Ctrl+Shift+Del or Cmd+Shift+Del)
- Check browser console for any image loading errors

**Logo looks distorted?**
- Ensure logo dimensions are square or slightly rectangular
- Check CSS styling in templates
- Verify image file quality

**Logo appears blurry?**
- Use SVG format for best scaling (no pixelation)
- Or use high-resolution PNG (2x the display size)

## Branding Throughout the App

The KGISL branding is integrated at:

### Header Text
- **Institution Name:** "KGISL Institute of Technology"
- **Portal Name:** "R&D Management Portal"
- **Subtitle Variations:**
  - Login page: "Excellence in Research & Development"
  - Signup page: "Excellence in Research & Development"
  - Success page: "Your account has been successfully created"

### Color Scheme
- **Primary Gradient:** Purple to violet (#667eea to #764ba2)
- **Success Color:** Green (#28a745)
- **Warning Color:** Yellow (#ffc107)
- **KGISL Blue:** #003366 (for custom modifications)
- **KGISL Gold:** #cc9900 (for custom modifications)

## Customization

### Add Logo to Dashboard Pages

To add the logo to dashboard pages, edit `templates/dashboard.html` and add:

```html
<img src="{{ url_for('static', filename='images/kgisl_logo.png') }}" 
     alt="KGISL Logo" 
     style="height: 40px; margin-right: 10px;">
```

### Change Header Text

Update institution name in templates:
- `templates/base.html` - Line with "KGISL Institute of Technology"
- `templates/login.html` - Brand header section
- `templates/signup.html` - Brand header section

### Customize Colors

Modify CSS variables in `static/style.css`:

```css
:root {
    --kgisl-blue: #003366;      /* KGISL primary blue */
    --kgisl-gold: #cc9900;      /* KGISL accent gold */
    --primary-color: #667eea;   /* Current primary */
    --secondary-color: #764ba2; /* Current secondary */
}
```

## File Structure

```
R&D Manger/
├── static/
│   ├── images/
│   │   ├── kgisl_logo.svg      (Placeholder - Replace with actual logo)
│   │   └── kgisl_logo.png      (Add your PNG logo here)
│   ├── style.css               (Main stylesheet)
│   └── calendar.js
├── templates/
│   ├── base.html               (Navbar with logo)
│   ├── login.html              (Login page with logo)
│   ├── signup.html             (Signup page with logo)
│   ├── registration_success.html (Welcome page with logo)
│   ├── dashboard.html
│   ├── admin_dashboard.html
│   ├── thank_you.html
│   └── ...
└── app.py
```

## Need Help?

For questions about logo implementation or branding customization, contact the development team or check the main README.md file.

---

**Last Updated:** January 20, 2026
**Version:** 1.0
