# Quick Deployment Guide 🚀

## TL;DR - Deploy in 10 Minutes

### Backend (Render) - 5 minutes

1. **Go to Render**: https://dashboard.render.com
2. **New Web Service** → Connect GitHub repo
3. **Settings**:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt && python manage.py migrate`
   - Start: `gunicorn task_analyzer.wsgi:application`
4. **Environment Variables**:
   ```
   SECRET_KEY = <generate-random-key>
   DEBUG = False
   ALLOWED_HOSTS = your-app.onrender.com
   ```
5. **Deploy** → Copy the URL (e.g., `https://task-analyzer.onrender.com`)

### Frontend (Vercel) - 5 minutes

1. **Go to Vercel**: https://vercel.com/dashboard
2. **New Project** → Import GitHub repo
3. **Settings**:
   - Root Directory: `frontend`
   - Framework: Other
4. **Before Deploy**: Update `frontend/index.html` line 8:
   ```javascript
   window.API_BASE_URL = 'https://your-render-url.onrender.com/api';
   ```
5. **Deploy** → Done!

### Update CORS

1. Go back to Render
2. Add environment variable:
   ```
   CORS_ALLOWED_ORIGINS = https://your-vercel-app.vercel.app
   ```
3. Save → Auto-redeploys

---

## Generate SECRET_KEY

Run this in your terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## That's it! 🎉

Your app should be live at your Vercel URL!


