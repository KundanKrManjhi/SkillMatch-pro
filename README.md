# SkillMatch Pro — Resume & Job Matching Platform

A modular full-stack career platform built with **React + Vite**, **FastAPI**, and **MongoDB**. It includes separate candidate/admin workspaces, registration and login, resume scoring, profile editing, job/company management, application status tracking, support tickets, and an admin activity log.

## Features

### Candidate workspace
- User registration, login and logout.
- Editable profile: education, experience, skills, target role and location.
- PDF resume upload and replacement; the app validates **400 KB minimum** and **10 MB maximum**.
- Resume text extraction, structural score, detected skill keywords, section checklist and improvement suggestions.
- Job search by title/company/skill and location.
- Apply to jobs, save jobs, see application status and compare skills against listings.
- Submit help desk tickets and track their status.

### Admin workspace
- Separate Admin login option and role-protected routes/API endpoints.
- Dashboard counts for registered users, jobs, companies, applications, resume uploads, form events and open support tickets.
- Add/delete companies, publish/deactivate jobs, review users and update application status.
- Audit log for registrations, logins/logouts, profile updates, resume uploads, application submits and support forms.
- Review and update support tickets.

### Structure
```text
SkillMatch_Pro_Project/
├── backend/
│   ├── app/
│   │   ├── main.py, config.py, database.py, schemas.py, security.py, seed.py
│   │   └── routers/ (auth, profile, resumes, jobs, admin, support)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/ (Layout, UI)
    │   └── pages/ (separate user and admin pages)
    ├── package.json
    └── .env.example
```

## Prerequisites
- Python 3.10+ (Python 3.11 or 3.12 recommended)
- Node.js 20+
- MongoDB Community Server running locally, or a MongoDB Atlas connection string

## Windows PowerShell setup (run these steps in order)

### 1. Configure MongoDB and backend
Open a PowerShell terminal in the project folder:

```powershell
cd backend
Copy-Item .env.example .env
```

Open `backend/.env` and set `MONGODB_URL` if your MongoDB URI is different. Change `JWT_SECRET_KEY` and `ADMIN_PASSWORD` before using this outside your own machine. The default local development admin is:

- Email: `admin@skillmatch.local`
- Password: `ChangeMe123!`

You can change both in `backend/.env` **before** running the seed command. The seed command creates the initial admin only if that email does not already exist.

Create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.seed
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Keep this terminal open. API docs: http://127.0.0.1:8000/docs
Health check: http://127.0.0.1:8000/api/health

> If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. Do not close the backend terminal while using the frontend.

### 2. Start the frontend in a second terminal
Open a **new** PowerShell terminal in the project folder:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open the Local URL shown by Vite (normally http://127.0.0.1:5173). Keep this terminal open too.

### 3. Login
- Candidate: select **User** and create an account using **Create an account**.
- Admin: select **Admin** on the login screen and use the credentials configured in `backend/.env`.
- Use the sidebar **Sign out** button to log out. JWT is removed from browser local storage and a logout event is logged.

## MongoDB collections
The app uses the database name configured by `DATABASE_NAME` (default `smart_skill_job`) and these collections: `users`, `companies`, `jobs`, `resumes`, `applications`, `saved_jobs`, `tickets`, and `audit`.

## Important notes
- Resume scoring is a transparent heuristic based on text, common skills and section presence. It is not an official ATS score and cannot guarantee interview selection.
- The PDF analyzer extracts text-based PDFs. Scanned/image-only or password-protected PDFs may be rejected if readable text cannot be extracted.
- Job listings and employers seeded by the project are **sample/demo data**. Verify real openings on the employer's official careers page.
- This project stores user data and resume text in MongoDB. Do not deploy publicly without setting strong secrets, HTTPS, rate limiting, backups, privacy controls and an appropriate retention policy.
