# GulfTalent — UAE Jobs Platform

A full-stack job board where Kenyan professionals apply for UAE career opportunities. No account needed to apply. Admin controls job listings, required documents per career category, and all applications. Automated emails fire on every submission and status change.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Bootstrap Icons (CDN), Custom CSS |
| Backend | Django 4.2 + Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | SQLite (dev) → PostgreSQL (production) |
| Email | Django SMTP (`EmailMultiAlternatives` + HTML templates) |
| File Uploads | Django `FileField` + Pillow |
| Filtering | `django-filter` + DRF SearchFilter |

---

## Full Project Structure

```
gulftalent/
│
├── README.md
│
├── gulftalent_backend/               # Django project root
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── gulftalent_backend/           # Project config
│   │   ├── settings.py
│   │   ├── urls.py                   # Mounts /api/ and /django-admin/
│   │   ├── api_urls.py               # ALL API endpoints documented + wired
│   │   └── wsgi.py
│   │
│   ├── accounts/                     # Custom AdminUser model + JWT auth
│   │   ├── models.py                 # AdminUser (email-based, no username)
│   │   ├── serializers.py
│   │   ├── views.py                  # Login, Logout, Me
│   │   └── admin.py
│   │
│   ├── categories/                   # Job categories + required documents config
│   │   ├── models.py                 # Category, RequiredDocument
│   │   ├── serializers.py
│   │   ├── views.py                  # Public + Admin views
│   │   └── admin.py
│   │
│   ├── jobs/                         # Job listings
│   │   ├── models.py                 # Job (slug, SEO, emirate, salary, etc.)
│   │   ├── serializers.py
│   │   ├── filters.py                # JobFilter (emirate, type, category, salary)
│   │   ├── views.py                  # Public list/detail + Admin CRUD + toggles
│   │   ├── dashboard_views.py        # Admin stats endpoint
│   │   └── admin.py
│   │
│   ├── applications/                 # Job applications (no account required)
│   │   ├── models.py                 # Application, UploadedDocument
│   │   ├── serializers.py
│   │   ├── filters.py
│   │   ├── views.py                  # Submit + Admin list/detail/status/export
│   │   ├── document_views.py         # Admin manage required docs
│   │   └── admin.py
│   │
│   └── core/
│       ├── email_service.py          # All email sending (received, notify admin, status update)
│       ├── utils/
│       │   └── pagination.py         # Standard paginator with meta
│       └── email_templates/
│           ├── application_received.html     # → Applicant on submit
│           ├── application_admin_notify.html  # → Admin on new app
│           └── status_update.html             # → Applicant on status change
│
└── frontend/                         # React 18 SPA (next phase)
    ├── index.html
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── services/api.js
    │   ├── styles/main.css
    │   ├── components/
    │   └── pages/
```

---

## API Endpoints

### Public (no auth)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/jobs/` | List jobs — filter by `emirate`, `job_type`, `category`, `experience_level`, search by title |
| GET | `/api/jobs/featured/` | Featured jobs (max 6) |
| GET | `/api/jobs/<slug>/` | Single job detail with full content |
| GET | `/api/categories/` | All active categories with job counts |
| GET | `/api/categories/<slug>/` | Category detail + required documents |
| GET | `/api/categories/<slug>/documents/` | Required documents list for a category |
| POST | `/api/applications/` | Submit application — multipart/form-data with file uploads |

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login/` | `{email, password}` → `{access, refresh}` |
| POST | `/api/auth/refresh/` | `{refresh}` → `{access}` |
| POST | `/api/auth/logout/` | `{refresh}` → blacklist token |
| GET | `/api/auth/me/` | Current admin info (Bearer required) |

### Admin (Bearer token required)

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/admin/jobs/` | List all jobs / Create job |
| GET/PUT/DELETE | `/api/admin/jobs/<id>/` | Job detail / Update / Delete |
| POST | `/api/admin/jobs/<id>/toggle-featured/` | Toggle featured flag |
| POST | `/api/admin/jobs/<id>/toggle-active/` | Toggle active flag |
| GET/POST | `/api/admin/categories/` | List / Create category |
| GET/PUT/DELETE | `/api/admin/categories/<id>/` | Category detail / Update / Delete |
| GET/POST | `/api/admin/documents/` | List / Create required document (filter `?category=<id>`) |
| GET/PUT/DELETE | `/api/admin/documents/<id>/` | Document detail / Update / Delete |
| GET | `/api/admin/applications/` | List all applications (filter by status, job, category, date) |
| GET | `/api/admin/applications/<id>/` | Full application + uploaded files |
| PUT | `/api/admin/applications/<id>/status/` | Update status + admin notes → triggers email |
| GET | `/api/admin/applications/export/` | CSV download |
| GET | `/api/admin/dashboard/stats/` | Counts for jobs, categories, applications |

---

## Application File Upload Convention

`POST /api/applications/` accepts `multipart/form-data`.

File fields should be named `doc_<required_document_id>` for known required docs, or `doc_extra_1`, `doc_extra_2` for additional files. For each file field, optionally include `doc_<id>_label` with a display name.

```
first_name=John
last_name=Doe
email=john@example.com
...
doc_3=<file: passport.pdf>
doc_3_label=Passport Copy
doc_5=<file: cv.pdf>
doc_5_label=CV / Resume
```

---

## Email Flow

| Trigger | To | Template |
|---|---|---|
| Application submitted | Applicant | `application_received.html` |
| Application submitted | Admin | `application_admin_notify.html` |
| Admin changes status | Applicant | `status_update.html` |

Set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in dev to see emails printed to terminal.

---

## Getting Started

```bash
cd gulftalent_backend
pip install -r requirements.txt
cp .env.example .env          # edit vars as needed
python manage.py migrate
python manage.py createsuperuser   # or use the one pre-created below
python manage.py runserver
```

**Default admin created during setup:**
- Email: `admin@gulftalent.co.ke`
- Password: `Admin@1234!`
- ⚠️ Change this immediately in production

**Django admin panel:** `http://localhost:8000/django-admin/`
**API base:** `http://localhost:8000/api/`

---

## Models Overview

```
AdminUser         — email, full_name, is_staff, is_superuser
Category          — name, slug, description, image, icon, seo_*, is_active, order
RequiredDocument  — category FK, label, description, accepted_file_types, is_required, order
Job               — title, slug, category FK, emirate, job_type, experience_level,
                    salary_min, salary_max, salary_display, description, requirements,
                    responsibilities, benefits, image, is_featured, is_active, is_urgent,
                    seo_title, seo_description, seo_keywords, expires_at
Application       — job FK, first_name, last_name, email, phone, nationality,
                    date_of_birth, gender, current_location, cover_letter,
                    years_of_experience, highest_education, linkedin_url,
                    status, admin_notes, ip_address
UploadedDocument  — application FK, required_document FK, label, file, file_name,
                    file_size, file_type
```