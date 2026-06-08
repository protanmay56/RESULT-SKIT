# SKIT Examination Portal

A complete Flask + MySQL web application for managing student exam results — modelled after skitexam.com.

---

## Features

- **Homepage** — 3D flip card role selector (Student / Admin)
- **Student login** — Roll Number + Date of Birth authentication
- **Student dashboard** — Subject-wise marksheet, SGPA, percentage, Pass/Fail/Back status, semester switcher, print
- **Admin panel** — Sidebar layout with Dashboard, Upload Result, All Results, Student Registry
- **Upload result** — Dynamic subject rows, auto-fill from existing students, publish/unpublish toggle
- **Dark mode** — Persisted via localStorage

---

## Tech Stack

| Layer     | Technology                  |
|-----------|-----------------------------|
| Backend   | Python 3.10+ / Flask 3      |
| Database  | MySQL 8 via SQLAlchemy      |
| Frontend  | Jinja2 templates, Vanilla JS, Custom CSS |
| Auth      | Session-based (Werkzeug hashed passwords) |
| Deploy    | Gunicorn + Nginx (or Railway/Render) |

---

## Local Setup

### 1. Clone / download the project

```bash
cd skit_portal
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up MySQL

Make sure MySQL is running, then:

```bash
mysql -u root -p < schema.sql
```

This creates the `skit_portal` database and tables.

### 5. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:

```
SECRET_KEY=any-long-random-string
DB_USER=root
DB_PASS=your_mysql_password
DB_HOST=localhost
DB_NAME=skit_portal
```

### 6. Run the app

```bash
python app.py
```

Visit: **http://localhost:5000**

The first run automatically creates the admin account:
- Username: `admin`
- Password: `admin123`

**Change the admin password** after first login (update in MySQL or add a change-password route).

---

## Usage Guide

### Admin Workflow

1. Go to `http://localhost:5000` → click **College** card
2. Login: `admin` / `admin123`
3. Click **Upload Result** in the sidebar
4. Fill student info (Roll No, Name, DOB, Branch, Semester)
5. Enter marks for each subject
6. Click **Upload Result** → student can now login and view results

### Student Workflow

1. Go to homepage → click **Student** card
2. Enter Roll Number + Date of Birth (set by admin) + Semester
3. View subject-wise marksheet with SGPA, percentage, Pass/Fail/Back

---

## Deployment on Railway (Free)

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add a **MySQL** plugin
4. Set environment variables in Railway dashboard:
   ```
   SECRET_KEY=your-secret
   DB_USER=<from Railway MySQL>
   DB_PASS=<from Railway MySQL>
   DB_HOST=<from Railway MySQL>
   DB_NAME=railway
   ```
5. Railway auto-detects `gunicorn` and runs the app

**Start command** (set in Railway): `gunicorn app:app`

---

## Deployment on Render (Free)

1. Push to GitHub
2. New Web Service → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add a **PostgreSQL** instance (or use external MySQL)
6. Set env vars in Render dashboard

---

## Deployment with Nginx + Gunicorn (VPS)

```bash
# Install
pip install gunicorn

# Run (production)
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Nginx config (/etc/nginx/sites-available/skit)
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/skit_portal/static;
    }
}
```

---

## Project Structure

```
skit_portal/
├── app.py                    # Flask app, routes, models
├── requirements.txt
├── schema.sql                # MySQL schema
├── .env.example
├── templates/
│   ├── base.html             # Base layout (nav, flash, dark toggle)
│   ├── index.html            # Homepage with flip cards
│   ├── student_login.html
│   ├── student_dashboard.html
│   ├── admin_login.html
│   ├── admin_base.html       # Admin layout with sidebar
│   ├── admin_dashboard.html
│   ├── admin_upload_result.html
│   ├── admin_results.html
│   ├── admin_students.html
│   └── admin_add_student.html
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## Default Credentials

| Role    | Username / Roll | Password / DOB |
|---------|-----------------|----------------|
| Admin   | admin           | admin123       |
| Student | (set per upload)| DOB set by admin |

---

## Customization

- **College name / branding**: edit `templates/index.html` and `base.html`
- **Add more branches**: update the `<select>` options in upload and add-student templates
- **Pass criteria**: edit the `status` property in the `Subject` model in `app.py`
- **Add email OTP login**: replace the DOB check with OTP via Flask-Mail
- **Admit card PDF**: add a route using `reportlab` or `weasyprint` to generate a PDF

---

## License

Private/personal use. Do not redistribute with SKIT branding.
