# FreshMart — Deployment Guide

Two supported paths: **Docker Compose** (self-hosted, one command) or **Render + Vercel** (managed, matches the original spec).

---

## Option A — Docker Compose (self-hosted)

Everything — Postgres, Redis, Django/Gunicorn, Celery worker + beat, the built React app, and an Nginx reverse proxy — runs from one file.

```bash
cp backend/.env.example backend/.env   # fill in real SECRET_KEY, email, payment keys
docker compose up --build -d
docker compose exec backend python manage.py createsuperuser
```

- App: `http://localhost/`
- Admin: `http://localhost/admin/`
- API: `http://localhost/api/v1/`
- Swagger: `http://localhost/api/docs/`

Services (see `docker-compose.yml`): `db` (Postgres 16), `redis` (Redis 7), `backend` (Gunicorn, auto-runs `migrate` + `collectstatic` on boot), `celery_worker`, `celery_beat`, `frontend` (Nginx serving the Vite build), `nginx` (reverse proxy routing `/api`, `/admin`, `/static`, `/media` to the backend and everything else to the frontend).

To rebuild after code changes: `docker compose up --build -d`. To view logs: `docker compose logs -f backend`. To tear down: `docker compose down` (add `-v` to also drop the Postgres volume).

**Production hardening before going live:**
- Set `DEBUG=False` and a real `SECRET_KEY` in `backend/.env`
- Put the whole stack behind HTTPS (e.g. Caddy or an external load balancer terminating TLS in front of the `nginx` service, or a managed cert via your host)
- Set `CORS_ALLOWED_ORIGINS` to your real domain
- Point `DEFAULT_FILE_STORAGE` at Cloudinary (`USE_CLOUDINARY=True`) so uploaded media survives container restarts, or mount a persistent volume for `/app/media`

---

## Option B — Render (backend) + Vercel (frontend), per the original spec

### Backend on Render
1. Push this repo to GitHub.
2. New → **Web Service** on Render, point at `/backend`.
3. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
5. Add a **Render PostgreSQL** instance and a **Render Redis** instance (or Upstash), then set env vars from `.env.example` using their connection strings (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `REDIS_URL`).
6. Set `ALLOWED_HOSTS` to your `.onrender.com` domain, `DEBUG=False`, `SECRET_KEY` to a real secret, `CORS_ALLOWED_ORIGINS` to your Vercel domain.
7. Add a Render **Background Worker** running `celery -A config worker --loglevel=info` and a **Cron Job / Worker** for `celery -A config beat --loglevel=info`, both pointed at the same repo/env.
8. After first deploy, open a shell and run `python manage.py migrate && python manage.py createsuperuser`.

### Frontend on Vercel
1. Import the repo, set the project root to `/frontend`.
2. Framework preset: Vite. Build command: `npm run build`. Output dir: `dist`.
3. Env var: `VITE_API_URL=https://<your-render-service>.onrender.com/api/v1`.
4. Deploy.

### Media — Cloudinary
1. Create a free Cloudinary account, grab `cloud_name`, `api_key`, `api_secret`.
2. On Render, set `USE_CLOUDINARY=True` plus `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET`.
3. All `ImageField` uploads (products, categories, reviews, profile photos) automatically route to Cloudinary — no code changes needed, it's a storage backend swap in `settings.py`.

### Database — PostgreSQL
Both paths use Postgres as the system of record; SQLite is never used in this project (Postgres-specific features like `JSONField` aggregation and UUID PKs are assumed).

### Optional — Amazon S3
The spec lists S3 as optional additional storage. If you'd rather use S3 than Cloudinary, swap `DEFAULT_FILE_STORAGE` to `storages.backends.s3boto3.S3Boto3Storage` (`pip install django-storages boto3`) and set the usual `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_STORAGE_BUCKET_NAME` env vars — not wired by default since Cloudinary is the primary path.

---

## Environment variables reference
See `backend/.env.example` for the full list. Never commit a real `.env` — it's already covered by `.dockerignore`; add it to `.gitignore` too if you haven't.

## CI/CD
`.github/workflows/ci.yml` runs on every push/PR: Django checks + `makemigrations --check` + `manage.py test` against a real Postgres+Redis service container, a frontend `npm run build`, and finally builds both Docker images to catch Dockerfile regressions. Wire a deploy step (Render/Vercel both support git-push auto-deploy, so in practice CI just needs to pass — no extra step required beyond enabling auto-deploy in each dashboard).
