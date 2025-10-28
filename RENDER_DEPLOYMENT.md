# Deploy to Render.com - Step by Step Guide

## Prerequisites
1. GitHub account
2. Render.com account (sign up at https://render.com)

## Steps to Deploy

### 1. Initialize Git and Push to GitHub

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: CAMS2CSV API"

# Create repository on GitHub (via web or CLI)
# If using GitHub CLI:
gh repo create cams2csv --public --source=. --remote=origin --push

# Or manually:
# 1. Go to https://github.com/new
# 2. Create a new repository named "cams2csv"
# 3. Then run:
git remote add origin https://github.com/YOUR_USERNAME/cams2csv.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render.com

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Sign in or create account

2. **Create New Web Service:**
   - Click "New +" button
   - Select "Web Service"

3. **Connect GitHub Repository:**
   - Click "Connect GitHub" 
   - Authorize Render to access your repositories
   - Select "cams2csv" repository

4. **Configure Service:**
   - **Name:** `cams2csv-api` (or your preferred name)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** Leave empty (uses root)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`
   
   **Note:** Render will auto-detect from `render.yaml`, so most settings are pre-filled!

5. **Select Plan:**
   - Choose **Free** plan for testing
   - Can upgrade later if needed

6. **Click "Create Web Service"**

### 3. Wait for Deployment

- Build will take 5-10 minutes on first deploy
- You can watch progress in the "Logs" tab
- On successful deployment, you'll get a URL like: `https://cams2csv-api.onrender.com`

### 4. Test Your API

Once deployed, test your API:

```bash
# Check API docs
curl https://your-service.onrender.com/docs

# Or open in browser
open https://your-service.onrender.com/docs
```

## Environment Variables (Optional)

If you need to add environment variables:
1. Go to your service dashboard
2. Click "Environment"
3. Add variables as needed
4. Service will automatically restart

## Post-Deployment

### Update Your Code

```bash
# Make changes
git add .
git commit -m "Updated code"
git push

# Render automatically rebuilds and deploys!
```

### View Logs

- Go to your service dashboard on Render
- Click "Logs" tab
- Real-time logs are shown

### Monitor Service

- Free tier services spin down after 15 minutes of inactivity
- They automatically spin up on next request (may take 30-60 seconds)
- Upgrade to paid plan for always-on service

## Troubleshooting

### Build Fails

Check logs for:
- Missing dependencies in requirements.txt
- Python version compatibility
- Build command errors

### Service Not Starting

Check logs:
- Port configuration correct?
- Start command is correct?
- Environment variables set?

### Service is Slow to Respond

- Free tier services spin down after inactivity
- First request after spin-down takes longer
- Consider upgrading for production use

## Upgrading to Paid Plan (Optional)

If you need:
- Always-on service (no spin-down)
- More memory/CPU
- Better performance
- Priority support

1. Go to service dashboard
2. Click "Change Plan"
3. Select paid tier
4. Enter payment method

## API Endpoints After Deployment

Once deployed, your API will be available at:

- **Root:** `https://your-service.onrender.com/`
- **API Docs:** `https://your-service.onrender.com/docs`
- **ReDoc:** `https://your-service.onrender.com/redoc`
- **Parse Endpoint:** `https://your-service.onrender.com/parse`

## Benefits of Render.com

✅ Free tier available
✅ Automatic HTTPS/SSL
✅ Auto-deployment from GitHub
✅ Built-in logging
✅ No server management needed
✅ Automatic scaling
✅ Environment variable management
✅ Simple configuration

## Next Steps

1. Test your deployed API
2. Share the API URL with your team
3. Integrate into your applications
4. Monitor usage in Render dashboard

