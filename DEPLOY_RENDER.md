# Deploy Backend to Render

## 1. Create a new project

1. Go to [render.com](https://render.com) and sign in
2. **New** → **Web Service** → **Build and deploy from a Git repository**
3. Connect your GitHub repository

## 2. Configure the Web Service

- **Name**: `fairshare-api`
- **Environment**: `Python 3`
- **Region**: Choose nearest region
- **Branch**: `main`
- **Root Directory**: Leave empty (if backend is in root) or set to `backend`

## 3. Build Settings

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

## 4. Add Databases

### PostgreSQL
1. **New** → **PostgreSQL**
2. **Name**: `fairshare-db`
3. **Database Name**: `fairshare`
4. **User**: `fairshare_user`
5. **Plan**: Free

### Redis
1. **New** → **Redis**
2. **Name**: `fairshare-redis`
3. **Plan**: Free

## 5. Environment Variables

In your web service → **Environment**, add these variables:

### Required Variables
| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | Auto-set by Render PostgreSQL | Connection string |
| `REDIS_URL` | Auto-set by Render Redis | Connection string |
| `SECRET_KEY` | Generate with `openssl rand -hex 32` | JWT signing key |
| `CORS_ORIGINS` | `https://your-frontend-domain.com` | Frontend URL |

### Optional Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `PYTHON_VERSION` | `3.12.7` | Python version |

## 6. Database Connection

Render automatically sets these environment variables:

- **PostgreSQL**: `DATABASE_URL` with format: `postgresql://user:password@host:port/dbname`
- **Redis**: `REDIS_URL` with format: `redis://host:port`

## 7. Deploy

1. Click **Create Web Service**
2. Render will automatically build and deploy
3. Monitor logs in the **Logs** tab

## 8. Get Your URLs

After deployment:
- **API URL**: `https://fairshare-api.onrender.com`
- **API Docs**: `https://fairshare-api.onrender.com/docs`
- **Database**: Available in PostgreSQL service dashboard

## 9. (Optional) Add Custom Domain

1. Go to **Custom Domains** in your web service
2. Add your domain (e.g., `api.yourapp.com`)
3. Update DNS records as instructed

## 10. (Optional) Celery Worker

For background tasks (trust score, analytics):

1. **New** → **Web Service**
2. Same repository, but **Start Command**: `celery -A app.workers.celery_app worker --loglevel=info`
3. Add same environment variables as main service
4. Set as **Background Worker** type

## Troubleshooting

### Common Issues
- **Database connection**: Ensure `DATABASE_URL` is correctly set
- **CORS errors**: Check `CORS_ORIGINS` includes your frontend URL
- **Build failures**: Check Python version compatibility

### Health Check
The `/health` endpoint should return: `{"status": "ok"}`

### Logs
Monitor deployment and runtime logs in the Render dashboard.
