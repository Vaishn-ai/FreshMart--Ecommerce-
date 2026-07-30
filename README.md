<<<<<<< HEAD
# FreshMart

A production-ready grocery e-commerce platform — Django 5 + DRF backend, React 19 + Vite frontend, PostgreSQL, Redis, Celery, JWT auth, Cloudinary media, and a full Docker deployment story.

Built and statically audited across 9 phases (foundation → cart/wishlist/coupons → checkout/payments → orders/tracking → reviews/Q&A → admin dashboard → advanced search → performance/accessibility → Docker/CI). See `docs/PROJECT_REPORT.md` for the full build history and audit findings.

## Stack

**Backend:** Python 3.13, Django 5, DRF, PostgreSQL, Redis, Celery, JWT (SimpleJWT), Pillow, django-filter, Cloudinary, CORS, WhiteNoise, Gunicorn, Razorpay/Stripe SDKs, ReportLab (PDF invoices)
**Frontend:** React 19, Vite, React Router, Axios, Context API, React Hook Form, Framer Motion, Swiper, React Icons, Tailwind CSS, react-helmet-async (SEO)
**Deployment:** Docker Compose (self-hosted) or Render (backend) + Vercel (frontend), Nginx, PostgreSQL, Cloudinary, GitHub Actions CI

## SEO

- **Per-page meta tags** — title, description, canonical URL, Open Graph, Twitter Card via a reusable `<SEO>` component (`frontend/src/components/SEO.jsx`) built on `react-helmet-async`, wired into all 16 pages
- **Structured data (JSON-LD)** — `Product` schema (price, availability, rating) on product detail pages, `WebSite` on the homepage, `FAQPage` on the FAQ page — these power rich results in search
- **Live sitemap** — `/sitemap.xml` is a real Django view (`backend/config/seo.py`) generating XML from static pages plus every active product, with `lastmod` from the product's `updated_at`. Not a static file — it reflects the current catalog.
- **`robots.txt`** — served by the same Django view, points crawlers at the sitemap, disallows private routes (`/cart`, `/checkout`, `/orders`, `/profile`, auth pages, `/admin/`, `/api/`)
- **Same-origin in production** — the reverse-proxy nginx config routes `/sitemap.xml` and `/robots.txt` to the backend under the same domain the frontend is served from (see `deploy/nginx/default.conf`), which is what search engines expect
- **`noindex`** applied to private/account pages (cart, checkout, orders, profile, login, register, forgot-password, 404) and to search-filtered product listing URLs, so only real, canonical content gets indexed
- Open Graph share image (`frontend/public/og-image.png`) and favicon (`favicon.svg`) included

**Honest limitation:** this is a client-rendered Vite SPA, not server-side rendered. Google's crawler does execute JavaScript and can index SPA content, but less reliably and more slowly than SSR/SSG, and other crawlers (bots that don't run JS, some social media unfurlers) will only see the static `index.html` meta tags, not the per-page ones `react-helmet-async` injects after mount. If SEO becomes business-critical, the real fix is migrating to Next.js or adding a prerendering step (e.g. `vite-plugin-ssr`, prerender.io) — not something this project does today.

## Project layout

```
freshmart/
├── backend/            Django project — 11 apps (see below)
├── frontend/            React app — pages, components, contexts, services
├── deploy/nginx/         Reverse-proxy config for docker-compose
├── docs/               API docs, ER diagram, schema, guides, Postman collection
├── .github/workflows/    CI pipeline
└── docker-compose.yml    Full local stack in one command
```

### Backend apps
| App | Responsibility |
|---|---|
| `accounts` | Custom email-based User, JWT auth, addresses |
| `categories` | Categories/subcategories, brands |
| `products` | Catalog, variants, images, search/autocomplete/voice search, comparison |
| `cart` | Cart, save-for-later, coupon application, totals |
| `wishlist` | Wishlist, move-to-cart |
| `coupons` | Discount codes, usage limits |
| `orders` | Checkout, status timeline, PDF invoices |
| `payments` | Razorpay, Stripe, UPI, COD |
| `reviews` | Ratings, helpful votes, product Q&A, frequently-bought-together |
| `dashboard` | Admin analytics, inventory, low-stock alerts, CSV export |
| `notifications` | Celery tasks — email (live) and SMS (stubbed, integration-ready) |

## Quick start

### Option 1 — Docker Compose (recommended)
```bash
cp backend/.env.example backend/.env   # fill in SECRET_KEY, email, payment keys
docker compose up --build -d
docker compose exec backend python manage.py createsuperuser
```
Visit `http://localhost/`. API at `http://localhost/api/v1/`, Swagger at `http://localhost/api/docs/`, admin at `http://localhost/admin/`.

### Option 2 — Run backend and frontend separately
```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DB/Redis credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```
Requires a local PostgreSQL database and Redis server (or point `.env` at hosted ones).

### Running the Celery worker (for async email/SMS/low-stock tasks)
```bash
cd backend
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info   # if/when scheduled tasks are added
```

## Documentation
| Doc | Covers |
|---|---|
| [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) | Every endpoint, method, auth requirement, and payload shape |
| [`docs/ER_DIAGRAM.md`](docs/ER_DIAGRAM.md) | Mermaid entity-relationship diagram |
| [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | Field-by-field schema reference per app |
| [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) | Docker Compose *and* Render+Vercel deployment paths |
| [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md) | How to run the test suite, what's covered, manual QA checklist |
| [`docs/ADMIN_DATA_ENTRY_GUIDE.md`](docs/ADMIN_DATA_ENTRY_GUIDE.md) | Field-by-field walkthrough for adding categories/brands/products via the Django admin, plus a starter reference checklist |
| [`docs/postman_collection.json`](docs/postman_collection.json) | 54 requests across 9 folders, auto-saves JWT tokens on login |
| [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) | What's built, what's intentionally deferred and why, audit findings |

## Testing
```bash
cd backend
python manage.py test          # accounts, products, cart, orders have real APITestCase suites
```
CI (`.github/workflows/ci.yml`) runs this against real Postgres + Redis service containers on every push, plus a frontend build and a Docker build. See `docs/TESTING_GUIDE.md` for the full picture, including what isn't covered yet.

## Known gaps (documented, not hidden)
- **Google Login**: not wired up — no OAuth credentials were available. The `User.google_id` field is ready to receive it.
- **Real SMS delivery**: `notifications/tasks.py` has a working stub with a documented swap-in point for Twilio/MSG91/etc.
- **Test coverage**: `wishlist`, `coupons`, `payments`, `reviews`, `dashboard` don't have automated tests yet (`accounts`, `products`, `cart`, `orders` do).
- **Frontend automated tests**: none yet — manual QA checklist in the testing guide covers the gap for now.
- Full details and reasoning in `docs/PROJECT_REPORT.md`.

## A note on verification
This project was built and statically audited in a sandbox with no network access, so dependencies were never actually `pip install`-ed or `npm install`-ed here. Every `.py` and `.jsx`/`.js` file was verified for syntax correctness (`py_compile`, brace/paren balance), every cross-app model reference and URL include was checked for validity, every N+1 query pattern was manually reviewed and fixed where found (4 real bugs caught), and `docker-compose.yml`/the Postman collection were validated as well-formed YAML/JSON — but none of this replaces actually running `manage.py check`, `manage.py test`, or `npm run build` in a real environment. Do that as your first step after cloning.
=======
# FreshMart_Ecommerce
A full-stack grocery e-commerce application built with React, Django REST Framework, PostgreSQL, Vite, and Razorpay. Deployed using Vercel and Render.

# 🛒 FreshMart

FreshMart is a full-stack grocery e-commerce application designed to provide a fast, secure, and user-friendly online shopping experience. The project is built with **React (Vite)** for the frontend and **Django REST Framework** for the backend, using **PostgreSQL** as the database.

## ✨ Features

- 🔐 Secure Authentication with Email OTP Verification
- 👤 User Profile & Address Management
- 🛍️ Product Categories and Search
- ❤️ Wishlist Management
- 🛒 Shopping Cart
- 💳 Razorpay Payment Integration
- 📦 Order Tracking & Order History
- ⭐ Product Ratings & Reviews
- 📱 Fully Responsive Design
- ⚡ RESTful API Architecture

## 🛠️ Tech Stack

**Frontend**
- React
- Vite
- Axios
- React Router
- Framer Motion

**Backend**
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Gunicorn
- WhiteNoise

## 🚀 Deployment

- **Frontend:** Vercel
- **Backend:** Render
- **Database:** PostgreSQL (Render)
>>>>>>> cc84504c36870d11ff25d5870d7c210e2d1b1838
