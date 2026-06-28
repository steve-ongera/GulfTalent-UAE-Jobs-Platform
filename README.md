# GulfTalent — UAE Jobs Platform

A full-stack job board platform where Kenyan professionals apply for UAE career opportunities. No account required to apply. Admins control job listings, required documents per career category, and receive/manage applications. Automated emails sent on every application.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Bootstrap Icons (CDN), CSS (custom from Constra theme) |
| Backend | Node.js + Express (single core application) |
| Database | PostgreSQL (via Prisma ORM) |
| Email | Nodemailer (SMTP / SendGrid) |
| File Storage | Multer + local disk (or AWS S3 in production) |
| SEO | React Helmet Async |
| Image Handling | Sharp (resize/optimize) + slug-based URLs |

---

## Full Project Structure

```
gulftalent/
│
├── README.md
│
├── backend/                          # Single core Node/Express application
│   ├── package.json
│   ├── .env.example
│   ├── .gitignore
│   ├── server.js                     # Entry point — mounts all routes
│   │
│   ├── config/
│   │   ├── database.js               # Prisma client instance
│   │   ├── email.js                  # Nodemailer transporter config
│   │   └── storage.js                # Multer disk/S3 storage config
│   │
│   ├── prisma/
│   │   ├── schema.prisma             # All models: Job, Category, Application, Admin, Document
│   │   └── migrations/               # Auto-generated Prisma migrations
│   │
│   ├── routes/
│   │   ├── index.js                  # Mounts all route groups
│   │   ├── jobs.routes.js            # Public job routes
│   │   ├── categories.routes.js      # Public category routes
│   │   ├── applications.routes.js    # Public application submit route
│   │   ├── admin/
│   │   │   ├── auth.routes.js        # Admin login/logout/refresh
│   │   │   ├── jobs.routes.js        # Admin CRUD for jobs
│   │   │   ├── categories.routes.js  # Admin CRUD for categories
│   │   │   ├── documents.routes.js   # Admin manage required docs per category
│   │   │   └── applications.routes.js# Admin view/update/export applications
│   │   └── upload.routes.js          # File upload endpoint
│   │
│   ├── controllers/
│   │   ├── jobs.controller.js
│   │   ├── categories.controller.js
│   │   ├── applications.controller.js
│   │   ├── upload.controller.js
│   │   └── admin/
│   │       ├── auth.controller.js
│   │       ├── jobs.controller.js
│   │       ├── categories.controller.js
│   │       ├── documents.controller.js
│   │       └── applications.controller.js
│   │
│   ├── middleware/
│   │   ├── auth.middleware.js        # JWT verify for admin routes
│   │   ├── validate.middleware.js    # Joi/Zod request validation
│   │   ├── upload.middleware.js      # Multer file filter + limits
│   │   └── errorHandler.middleware.js
│   │
│   ├── services/
│   │   ├── email.service.js          # All email sending logic (templates)
│   │   ├── slug.service.js           # Generate/validate URL slugs
│   │   ├── image.service.js          # Sharp resize, webp conversion
│   │   └── seo.service.js            # Generate meta tags server-side (for SSR/OG)
│   │
│   ├── templates/                    # Nodemailer HTML email templates
│   │   ├── application-received.html # Email to applicant
│   │   ├── application-admin.html    # Email to admin on new app
│   │   └── status-update.html        # Email to applicant on status change
│   │
│   └── utils/
│       ├── pagination.js
│       ├── sanitize.js
│       └── constants.js
│
├── frontend/                         # React 18 SPA
│   ├── index.html                    # Root HTML — Bootstrap Icons CDN, meta base
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   │
│   ├── public/
│   │   ├── favicon.png
│   │   ├── og-image.jpg              # Default Open Graph image
│   │   └── robots.txt
│   │
│   └── src/
│       ├── main.jsx                  # ReactDOM.createRoot, BrowserRouter, HelmetProvider
│       ├── App.jsx                   # Route definitions (React Router v6)
│       │
│       ├── styles/
│       │   └── main.css              # Full Constra CSS + GulfTalent overrides
│       │
│       ├── services/
│       │   └── api.js                # All Axios API calls — every endpoint
│       │
│       ├── components/               # Reusable UI components
│       │   ├── Navbar.jsx
│       │   ├── Footer.jsx
│       │   ├── TopBar.jsx
│       │   ├── JobCard.jsx           # Job listing card with image, slug link, SEO
│       │   ├── JobFilter.jsx         # Filter by category, location, type
│       │   ├── ApplicationForm.jsx   # Multi-step form, dynamic doc uploads
│       │   ├── CategoryCard.jsx
│       │   ├── HeroSlider.jsx        # Banner carousel (Constra style)
│       │   ├── FactsCounter.jsx      # Animated counters section
│       │   ├── CallToAction.jsx
│       │   ├── TestimonialSlider.jsx
│       │   ├── NewsletterSignup.jsx
│       │   ├── SeoHead.jsx           # React Helmet wrapper per page
│       │   ├── Breadcrumb.jsx
│       │   ├── Pagination.jsx
│       │   ├── Spinner.jsx
│       │   ├── Alert.jsx
│       │   └── admin/
│       │       ├── AdminSidebar.jsx
│       │       ├── AdminTopbar.jsx
│       │       ├── DataTable.jsx
│       │       ├── JobForm.jsx
│       │       ├── CategoryForm.jsx
│       │       └── DocumentManager.jsx
│       │
│       └── pages/                    # One file per route
│           ├── Home.jsx              # /
│           ├── Jobs.jsx              # /jobs
│           ├── JobDetail.jsx         # /jobs/:slug
│           ├── Apply.jsx             # /jobs/:slug/apply
│           ├── ApplicationSuccess.jsx# /apply/success
│           ├── Categories.jsx        # /categories
│           ├── CategoryJobs.jsx      # /categories/:slug
│           ├── About.jsx             # /about
│           ├── Contact.jsx           # /contact
│           ├── NotFound.jsx          # *
│           └── admin/
│               ├── AdminLogin.jsx    # /admin/login
│               ├── AdminDashboard.jsx# /admin
│               ├── AdminJobs.jsx     # /admin/jobs
│               ├── AdminJobEdit.jsx  # /admin/jobs/new | /admin/jobs/:id/edit
│               ├── AdminCategories.jsx        # /admin/categories
│               ├── AdminDocuments.jsx         # /admin/documents
│               └── AdminApplications.jsx      # /admin/applications
│
└── docs/
    ├── api.md                        # Full API reference
    ├── email-flow.md                 # Email trigger map
    └── deployment.md                 # VPS / Docker deployment guide
```

---

## Database Models (Prisma Schema Overview)

```
Admin           — id, email, passwordHash, name, createdAt
Category        — id, name, slug, description, image, seoTitle, seoDesc, createdAt
RequiredDocument— id, categoryId, label, fileTypes[], isRequired, order
Job             — id, title, slug, categoryId, location, emirate, type, salary,
                  description, requirements, benefits, image, isFeatured,
                  isActive, seoTitle, seoDesc, seoKeywords, createdAt, expiresAt
Application     — id, jobId, firstName, lastName, email, phone, nationality,
                  coverLetter, status, appliedAt, updatedAt
UploadedDoc     — id, applicationId, documentLabel, filePath, fileType, fileSize
```

---

## API Endpoints (all in `services/api.js`)

### Public

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/jobs` | List jobs (paginated, filterable) |
| GET | `/api/jobs/:slug` | Single job by slug |
| GET | `/api/jobs/featured` | Featured jobs |
| GET | `/api/categories` | All categories |
| GET | `/api/categories/:slug` | Single category + its jobs |
| GET | `/api/categories/:slug/documents` | Required docs for a category |
| POST | `/api/applications` | Submit application (multipart) |
| POST | `/api/upload` | Upload a single document file |

### Admin (JWT protected)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/admin/auth/login` | Admin login → JWT |
| POST | `/api/admin/auth/logout` | Invalidate token |
| GET | `/api/admin/jobs` | List all jobs |
| POST | `/api/admin/jobs` | Create job |
| PUT | `/api/admin/jobs/:id` | Update job |
| DELETE | `/api/admin/jobs/:id` | Delete job |
| GET | `/api/admin/categories` | List categories |
| POST | `/api/admin/categories` | Create category |
| PUT | `/api/admin/categories/:id` | Update category |
| DELETE | `/api/admin/categories/:id` | Delete category |
| GET | `/api/admin/documents` | List required docs (by category) |
| POST | `/api/admin/documents` | Add required doc to category |
| PUT | `/api/admin/documents/:id` | Update required doc |
| DELETE | `/api/admin/documents/:id` | Remove required doc |
| GET | `/api/admin/applications` | List all applications (filter/sort) |
| GET | `/api/admin/applications/:id` | Single application + uploaded docs |
| PUT | `/api/admin/applications/:id/status` | Update status (reviewed/shortlisted/rejected) |
| GET | `/api/admin/applications/export` | CSV export |
| GET | `/api/admin/dashboard/stats` | Counts: jobs, apps, categories |

---

## Email Flow

| Trigger | Recipients | Template |
|---|---|---|
| Application submitted | Applicant + Admin | `application-received.html` / `application-admin.html` |
| Admin updates status | Applicant | `status-update.html` |

---

## Frontend Pages

| Route | Page | Description |
|---|---|---|
| `/` | Home | Hero slider, featured jobs, categories, facts, CTA |
| `/jobs` | Jobs | Searchable/filterable job listings with pagination |
| `/jobs/:slug` | Job Detail | Full job info, SEO meta, apply CTA |
| `/jobs/:slug/apply` | Apply | Dynamic form — fields + doc uploads based on category |
| `/apply/success` | Success | Confirmation page after submission |
| `/categories` | Categories | All career categories with images |
| `/categories/:slug` | Category Jobs | Jobs filtered by category |
| `/about` | About | Company info, mission |
| `/contact` | Contact | Contact form |
| `/admin/login` | Admin Login | — |
| `/admin` | Dashboard | Stats overview |
| `/admin/jobs` | Manage Jobs | Table with create/edit/delete |
| `/admin/categories` | Manage Categories | — |
| `/admin/documents` | Required Docs | Per-category document config |
| `/admin/applications` | Applications | View, filter, update status, export CSV |

---

## Key Features

- **No account required** — applicants fill form and submit directly
- **Dynamic document requirements** — admin sets which docs are needed per category (CV, passport copy, certificates, etc.)
- **Automated emails** — applicant receives confirmation; admin notified instantly
- **SEO** — every job and category has `slug`, `seoTitle`, `seoDescription`, `seoKeywords`, Open Graph tags
- **Image handling** — uploaded images auto-resized via Sharp, served with content-hash filenames
- **Admin panel** — full CRUD for jobs, categories, document rules; application inbox with status workflow
- **UAE Emirates filter** — filter jobs by emirate (Dubai, Abu Dhabi, Sharjah, etc.)

---

## Getting Started

### Backend
```bash
cd backend
cp .env.example .env          # fill DB_URL, JWT_SECRET, SMTP_* vars
npm install
npx prisma migrate dev
npm run dev
```

### Frontend
```bash
cd frontend
cp .env.example .env          # set VITE_API_BASE_URL
npm install
npm run dev
```

---

## Environment Variables

### Backend `.env`
```
DATABASE_URL=postgresql://user:pass@localhost:5432/gulftalent
JWT_SECRET=your_jwt_secret
JWT_EXPIRES_IN=7d
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your_sendgrid_key
EMAIL_FROM=noreply@gulftalent.co.ke
ADMIN_EMAIL=admin@gulftalent.co.ke
UPLOAD_DIR=uploads/
MAX_FILE_SIZE_MB=5
PORT=5000
```

### Frontend `.env`
```
VITE_API_BASE_URL=http://localhost:5000/api
```