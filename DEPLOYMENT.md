# 🚀 LearnTube AI Career Coach - Render Deployment Guide

This guide walks you through deploying the LearnTube AI Career Coach application on Render.

## 📋 Prerequisites

- [x] GitHub repository with your code
- [x] [Render account](https://render.com) (free tier available)
- [x] OpenRouter API key
- [x] Apify API token
- [x] Firebase service account JSON file

## 🎯 Quick Deployment (Automated)

### Option 1: One-Click Deploy with render.yaml

1. **Fork/Clone Repository**: Ensure your code is in GitHub
2. **Prepare Firebase Credentials**: Run the preparation script
   ```bash
   python scripts/prepare_firebase_for_render.py
   ```
3. **Deploy to Render**: 
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically deploy both services from `render.yaml`

### Option 2: Manual Service Creation

Follow the detailed steps below for more control over the deployment process.

---

## 🛠️ Detailed Deployment Steps

### Step 1: Prepare Firebase Credentials

Before deploying, you need to encode your Firebase credentials for secure environment variable storage:

```bash
# Run the preparation script
python scripts/prepare_firebase_for_render.py
```

This will:
- ✅ Find your Firebase credentials file
- ✅ Validate the JSON structure
- ✅ Encode to base64 format
- ✅ Save the encoded string to `firebase_credentials_base64.txt`

**Keep this encoded string handy** - you'll need it for environment variables.

### Step 2: Deploy Backend Service

1. **Create Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Backend Service**:
   ```
   Name: learntube-backend
   Environment: Python
   Branch: main
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Set Environment Variables**:
   ```
   OPENROUTER_API_KEY=sk-your-openrouter-key-here
   APIFY_API_TOKEN=your-apify-token-here
   FIREBASE_PROJECT_ID=learntube-18ce5
   FIREBASE_CREDENTIALS_BASE64=your-base64-encoded-credentials
   DEBUG=false
   ```

4. **Deploy**: Click "Create Web Service"

5. **Note Backend URL**: After deployment, copy the URL (e.g., `https://learntube-backend.onrender.com`)

### Step 3: Deploy Frontend Service

1. **Create Another Web Service**:
   - Click "New" → "Web Service"
   - Connect same repository

2. **Configure Frontend Service**:
   ```
   Name: learntube-frontend
   Environment: Python
   Branch: main
   Root Directory: frontend
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
   ```

3. **Set Environment Variables**:
   ```
   API_BASE_URL=https://learntube-backend.onrender.com
   ```
   *(Replace with your actual backend URL from Step 2)*

4. **Deploy**: Click "Create Web Service"

### Step 4: Update CORS Settings (If Needed)

If you get CORS errors, update your backend environment variables:

1. Go to your backend service in Render
2. Add/update environment variable:
   ```
   CORS_ORIGINS=https://your-frontend-url.onrender.com,https://*.onrender.com
   ```

---

## ✅ Testing Your Deployment

### Backend Health Check
Visit your backend URL: `https://learntube-backend.onrender.com`

You should see:
```json
{
  "message": "LearnTube AI Career Coach API",
  "version": "1.0.0",
  "status": "running"
}
```

### Frontend Access
Visit your frontend URL: `https://learntube-frontend.onrender.com`

You should see the Streamlit interface.

### End-to-End Test
1. Start a new session with a LinkedIn URL
2. Send a chat message
3. Verify the AI responds correctly

---

## 🔧 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check Python version
echo "python-3.11.0" > runtime.txt
```

#### Port Binding Errors
- ✅ Already fixed: The app now uses `$PORT` environment variable

#### CORS Errors
- ✅ Already fixed: Added production URLs to CORS origins

#### Firebase Connection Issues
- Check logs in Render dashboard
- Verify `FIREBASE_CREDENTIALS_BASE64` is set correctly
- Ensure the base64 string is complete (no line breaks)

#### Environment Variable Issues
```bash
# Test locally first
export API_BASE_URL=http://localhost:8000
streamlit run frontend/streamlit_app.py
```

### Viewing Logs

1. Go to Render Dashboard
2. Click on your service
3. View logs in the "Logs" tab
4. Check "Events" tab for deployment status

---

## 🎛️ Environment Variables Reference

### Backend Service (`learntube-backend`)
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API key | `sk-or-v1-xxxxx` |
| `APIFY_API_TOKEN` | ✅ | Apify scraping token | `apify_api_xxxxx` |
| `FIREBASE_PROJECT_ID` | ✅ | Firebase project ID | `learntube-18ce5` |
| `FIREBASE_CREDENTIALS_BASE64` | ✅ | Base64 encoded service account | `eyJ0eXBlIjoi...` |
| `DEBUG` | ❌ | Debug mode | `false` |

### Frontend Service (`learntube-frontend`)
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `API_BASE_URL` | ✅ | Backend service URL | `https://learntube-backend.onrender.com` |

---

## 🚀 Post-Deployment

### Custom Domains (Optional)
1. Go to service Settings → Custom Domains
2. Add your domain: `learntube.yourdomain.com`
3. Update DNS as instructed

### Monitoring
- Enable health checks (automatic on Render)
- Set up alerting for service downtime
- Monitor usage and performance

### Scaling
- Render automatically scales based on traffic
- Upgrade to Pro plan for better performance

---

## 💡 Tips for Success

1. **Test Locally First**: Ensure everything works before deploying
2. **Use Staging**: Test with production-like URLs first
3. **Monitor Costs**: Free tier has limitations
4. **Keep Secrets Safe**: Never commit API keys to repository
5. **Update Dependencies**: Keep requirements.txt current

---

## 🆘 Support

If you encounter issues:

1. **Check Logs**: Always start with service logs in Render dashboard
2. **Verify Environment Variables**: Ensure all required variables are set
3. **Test Locally**: Reproduce issues in local development
4. **Check Status**: Verify external services (OpenRouter, Apify, Firebase) are operational

---

## 🎯 Final Result

After successful deployment:
- **Backend API**: `https://learntube-backend.onrender.com`
- **Frontend App**: `https://learntube-frontend.onrender.com`  
- **Full Application**: Accessible worldwide with AI career coaching capabilities

Your LearnTube AI Career Coach is now live! 🌍✨ 