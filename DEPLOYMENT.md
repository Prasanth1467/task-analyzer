# Deployment Guide

This guide will help you deploy the Smart Task Analyzer:
- **Frontend** → Vercel
- **Backend** → Render

## Prerequisites

1. GitHub account
2. Vercel account (sign up at https://vercel.com)
3. Render account (sign up at https://render.com)
4. Git repository (GitHub, GitLab, or Bitbucket)

---

## Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

---

## Step 2: Deploy Backend to Render

### 2.1 Create a New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository containing your project

### 2.2 Configure the Service

**Basic Settings:**
- **Name**: `task-analyzer-backend` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend`
- **Environment**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && python manage.py migrate
  ```
- **Start Command**: 
  ```bash
  gunicorn task_analyzer.wsgi:application
  ```

### 2.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add:

```
SECRET_KEY = <generate-a-secure-random-key>
DEBUG = False
ALLOWED_HOSTS = your-app-name.onrender.com
CORS_ALLOWED_ORIGINS = https://your-vercel-app.vercel.app
```

**To generate SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2.4 Create PostgreSQL Database (Optional but Recommended)

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Name it: `task-analyzer-db`
3. Plan: **Free** (for testing)
4. Copy the **Internal Database URL**
5. Go back to your Web Service settings
6. Add environment variable:
   ```
   DATABASE_URL = <paste-the-internal-database-url>
   ```

**Note**: If you don't add DATABASE_URL, it will use SQLite (data may be lost on redeploy).

### 2.5 Deploy

1. Click **"Create Web Service"**
2. Wait for deployment to complete (5-10 minutes)
3. Copy your **Service URL** (e.g., `https://task-analyzer-backend.onrender.com`)

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Select the repository

### 3.2 Configure Project

**Project Settings:**
- **Framework Preset**: Other
- **Root Directory**: `frontend`
- **Build Command**: (leave empty - static files)
- **Output Directory**: `.` (current directory)

### 3.3 Add Environment Variables

Click **"Environment Variables"** and add:

```
VITE_API_BASE_URL = https://your-render-backend-url.onrender.com/api
```

**Replace** `your-render-backend-url.onrender.com` with your actual Render backend URL.

### 3.4 Update Frontend Code

**IMPORTANT**: Before deploying, you must update the API URL in `frontend/index.html`.

1. Open `frontend/index.html`
2. Find line 8 (the script tag with `window.API_BASE_URL`)
3. Replace `http://localhost:8000/api` with your Render backend URL:

```html
<script>
    // Update this line with your Render backend URL
    window.API_BASE_URL = 'https://your-render-backend-url.onrender.com/api';
</script>
```

**Example:**
If your Render URL is `https://task-analyzer-backend.onrender.com`, then:
```html
window.API_BASE_URL = 'https://task-analyzer-backend.onrender.com/api';
```

### 3.5 Deploy

1. Click **"Deploy"**
2. Wait for deployment (1-2 minutes)
3. Copy your **Vercel URL** (e.g., `https://task-analyzer.vercel.app`)

---

## Step 4: Update CORS Settings

After getting your Vercel URL, update the backend CORS settings:

1. Go to Render Dashboard → Your Web Service
2. Go to **"Environment"** tab
3. Update `CORS_ALLOWED_ORIGINS`:
   ```
   CORS_ALLOWED_ORIGINS = https://your-vercel-app.vercel.app
   ```
4. Click **"Save Changes"** (this will trigger a redeploy)

---

## Step 5: Test Your Deployment

1. **Test Backend API:**
   ```bash
   curl https://your-backend.onrender.com/api/tasks/suggest/
   ```

2. **Test Frontend:**
   - Open your Vercel URL in a browser
   - Try adding a task and analyzing it
   - Check browser console for any errors

---

## Troubleshooting

### Backend Issues

**Problem**: 500 Internal Server Error
- **Solution**: Check Render logs, ensure all environment variables are set
- Check: `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`

**Problem**: CORS errors
- **Solution**: Update `CORS_ALLOWED_ORIGINS` with your Vercel URL
- Ensure `CORS_ALLOW_ALL_ORIGINS = False` in production

**Problem**: Database connection errors
- **Solution**: Ensure `DATABASE_URL` is set correctly
- For PostgreSQL, ensure database is created and running

### Frontend Issues

**Problem**: API calls failing
- **Solution**: 
  1. Check `API_BASE_URL` in frontend code
  2. Verify backend URL is correct
  3. Check browser console for CORS errors
  4. Ensure backend CORS settings include your Vercel domain

**Problem**: 404 errors for static files
- **Solution**: Vercel should handle this automatically, but check `vercel.json` configuration

---

## Environment Variables Summary

### Backend (Render)

```
SECRET_KEY = <django-secret-key>
DEBUG = False
ALLOWED_HOSTS = your-app.onrender.com
CORS_ALLOWED_ORIGINS = https://your-vercel-app.vercel.app
DATABASE_URL = <postgresql-connection-string> (optional)
```

### Frontend (Vercel)

```
VITE_API_BASE_URL = https://your-backend.onrender.com/api
```

---

## Quick Deploy Commands

### Render (using Render CLI - Optional)

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy
```

### Vercel (using Vercel CLI)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
```

---

## Cost

- **Render Free Tier**: 
  - Web services: Free (spins down after 15 min inactivity)
  - PostgreSQL: Free (limited to 90 days)
  
- **Vercel Free Tier**:
  - Unlimited deployments
  - 100GB bandwidth/month
  - Perfect for this project

---

## Next Steps

1. Set up custom domains (optional)
2. Enable HTTPS (automatic on both platforms)
3. Set up monitoring/alerts
4. Configure database backups (for production)

---

## Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/

---

**Happy Deploying! 🚀**

