# Deploy Backend to Railway

## 1. Create a new project

1. Go to [railway.app](https://railway.app) and sign in
2. **New Project** → **Deploy from GitHub repo** (connect your repo first)

## 2. Configure root directory

If your repo root contains both `backend/` and `frontend/`, set:

- **Root Directory**: `backend`

## 3. Add services

In your project:

1. **PostgreSQL** – Click **+ New** → **Database** → **PostgreSQL**  
   - Railway sets `DATABASE_URL` automatically

2. **Redis** – Click **+ New** → **Database** → **Redis**  
   - Railway sets `REDIS_URL` automatically

## 4. Environment variables

In your backend service → **Variables**, add:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Generate a random string: `openssl rand -hex 32` |
| `CORS_ORIGINS` | Comma-separated frontend URLs, e.g. `https://yourapp.vercel.app` |

`DATABASE_URL` and `REDIS_URL` are set automatically when you add PostgreSQL and Redis.

## 5. Build & deploy

- **Build Command**: (auto-detected)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Release Command** (optional, for migrations): `alembic upgrade head`

Railway will auto-detect from `Procfile` or `railway.toml` if configured.

## 6. (Optional) Celery worker

To run background jobs (trust score, analytics):

1. **+ New** → **Empty Service**
2. Connect to same repo, Root Directory: `backend`
3. Start Command: `celery -A app.workers.celery_app worker --loglevel=info`
4. Add same env vars as the main service

## 7. Get your URL

After deploy, go to **Settings** → **Networking** → **Generate Domain** to get your public URL.
