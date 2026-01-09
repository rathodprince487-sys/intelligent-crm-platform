# 🚀 Free Deployment Guide - Intelligent CRM Platform

This guide provides **multiple FREE options** to deploy your CRM application so others can use it online.

---

## 📋 Table of Contents

1. [Quick & Easy: Tunneling (Temporary)](#option-1-quick--easy-tunneling-temporary)
2. [Best Free Option: Streamlit Community Cloud](#option-2-best-free-option-streamlit-community-cloud)
3. [Full Stack Deployment (Advanced)](#option-3-full-stack-deployment-advanced)
4. [Comparison Table](#comparison-table)

---

## Option 1: Quick & Easy: Tunneling (Temporary)

**Best for:** Quick demos, testing, temporary sharing  
**Pros:** Instant setup, no code changes needed  
**Cons:** Only works while your computer is on

### Method A: LocalTunnel (Recommended for Quick Sharing)

```bash
# 1. Make sure your app is running
# Terminal 1: Backend
node server.js

# Terminal 2: Frontend
python3 -m streamlit run app.py

# Terminal 3: Create public tunnel
npx localtunnel --port 8501
```

**You'll get a URL like:** `https://funny-cats-jump.loca.lt`

**Share this URL** with anyone! They can access your app instantly.

⚠️ **Note:** The URL changes each time you restart the tunnel.

---

### Method B: ngrok (More Stable)

```bash
# 1. Install ngrok
brew install ngrok

# 2. Create account at https://ngrok.com (free)

# 3. Authenticate (one-time setup)
ngrok config add-authtoken YOUR_AUTH_TOKEN

# 4. Create tunnel
ngrok http 8501
```

**You'll get a URL like:** `https://abc123.ngrok.io`

**Pros:**
- More stable than LocalTunnel
- Better performance
- Custom domains available (paid)

---

## Option 2: Best Free Option: Streamlit Community Cloud

**Best for:** Production deployment, permanent hosting  
**Pros:** Free, reliable, automatic updates from GitHub  
**Cons:** Requires GitHub account, some setup

### Step-by-Step Guide:

#### 1. Prepare Your Repository

```bash
# Create a GitHub repository (if you haven't already)
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 2. Create `requirements.txt`

Update your `requirements.txt` with all dependencies:

```txt
streamlit==1.50.0
pandas==2.3.3
plotly==5.24.1
openpyxl==3.1.5
requests==2.32.5
Pillow==11.3.0
scrapy==2.12.0
playwright==1.50.0
python-docx==1.2.0
```

#### 3. Create `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#0066CC"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1E1E1E"
textColor = "#FAFAFA"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
```

#### 4. Deploy to Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository
5. Set **Main file path:** `app.py`
6. Click **"Deploy"**

**Your app will be live at:** `https://your-app-name.streamlit.app`

#### 5. Handle Backend (Important!)

Since Streamlit Cloud only hosts the frontend, you have two options:

**Option A: Embed Backend in Streamlit (Recommended)**

Create a new file `streamlit_app.py`:

```python
import streamlit as st
import subprocess
import threading
import time

# Start Node.js backend in background
def start_backend():
    subprocess.Popen(['node', 'server.js'])

# Start backend once
if 'backend_started' not in st.session_state:
    threading.Thread(target=start_backend, daemon=True).start()
    time.sleep(2)  # Wait for backend to start
    st.session_state.backend_started = True

# Import and run your main app
exec(open('app.py').read())
```

**Option B: Deploy Backend Separately** (See Option 3)

---

## Option 3: Full Stack Deployment (Advanced)

**Best for:** Professional deployment with separate frontend/backend  
**All services are FREE!**

### Architecture:

```
Frontend (Streamlit Cloud) → Backend (Render.com) → Database (Supabase)
```

---

### Step 1: Database - Supabase (Free PostgreSQL)

#### 1.1 Create Supabase Account

1. Go to **https://supabase.com**
2. Sign up (free)
3. Create a new project
4. Note your **Database URL** from Settings → Database

#### 1.2 Migrate from SQLite to PostgreSQL

Update `database.js`:

```javascript
const { Sequelize } = require('sequelize');

// Use PostgreSQL instead of SQLite
const sequelize = new Sequelize(process.env.DATABASE_URL || 'postgresql://user:pass@host:5432/dbname', {
  dialect: 'postgres',
  dialectOptions: {
    ssl: {
      require: true,
      rejectUnauthorized: false
    }
  },
  logging: false
});

// Rest of your code remains the same...
```

Update `package.json`:

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "sequelize": "^6.35.0",
    "pg": "^8.11.0",
    "pg-hstore": "^2.3.4"
  }
}
```

---

### Step 2: Backend - Render.com (Free)

#### 2.1 Prepare Backend

Create `render.yaml`:

```yaml
services:
  - type: web
    name: crm-backend
    env: node
    buildCommand: npm install
    startCommand: node server.js
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: NODE_ENV
        value: production
```

#### 2.2 Deploy to Render

1. Go to **https://render.com**
2. Sign up (free)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name:** crm-backend
   - **Environment:** Node
   - **Build Command:** `npm install`
   - **Start Command:** `node server.js`
   - **Plan:** Free
6. Add environment variable:
   - `DATABASE_URL` = Your Supabase connection string
7. Click **"Create Web Service"**

**Your backend will be live at:** `https://crm-backend.onrender.com`

⚠️ **Note:** Free tier sleeps after 15 minutes of inactivity. First request may take 30-60 seconds.

---

### Step 3: Frontend - Streamlit Community Cloud

Update `app.py` to use the Render backend:

```python
import os

# Use environment variable for backend URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:3000')

# Replace all localhost:3000 references with BACKEND_URL
# Example:
response = requests.get(f'{BACKEND_URL}/api/leads')
```

Deploy to Streamlit Cloud (as described in Option 2), and add environment variable:
- `BACKEND_URL` = `https://crm-backend.onrender.com`

---

## Option 4: Alternative Free Platforms

### A. Railway.app (Full Stack)

**Free Tier:** 500 hours/month, $5 credit

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up
```

### B. Fly.io (Full Stack)

**Free Tier:** 3 VMs, 3GB storage

```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Launch app
fly launch

# 4. Deploy
fly deploy
```

### C. Vercel (Frontend Only)

**Free Tier:** Unlimited deployments

Good for static frontends, but requires serverless functions for backend.

---

## Comparison Table

| Platform | Type | Free Tier | Pros | Cons | Best For |
|----------|------|-----------|------|------|----------|
| **LocalTunnel** | Tunnel | Unlimited | Instant, no setup | Computer must stay on | Quick demos |
| **ngrok** | Tunnel | 1 tunnel | Stable, fast | Computer must stay on | Testing |
| **Streamlit Cloud** | Frontend | Unlimited | Easy, auto-deploy | Frontend only | Streamlit apps |
| **Render.com** | Backend | 750 hrs/month | Full stack support | Sleeps after 15min | Node.js backends |
| **Supabase** | Database | 500MB | PostgreSQL, realtime | Limited storage | Production DB |
| **Railway** | Full Stack | $5 credit | Easy setup | Credit runs out | Quick deployments |
| **Fly.io** | Full Stack | 3 VMs | Docker support | Complex setup | Advanced users |

---

## 🎯 Recommended Deployment Strategy

### For Quick Sharing (Today):
```bash
npx localtunnel --port 8501
```
✅ **5 minutes setup**

### For Production (This Week):

1. **Database:** Supabase (PostgreSQL)
2. **Backend:** Render.com
3. **Frontend:** Streamlit Community Cloud

✅ **Free forever**  
✅ **Professional setup**  
✅ **Auto-scaling**

---

## 📝 Quick Start Commands

### Option 1: LocalTunnel (Fastest)

```bash
# Terminal 1
node server.js

# Terminal 2
python3 -m streamlit run app.py

# Terminal 3
npx localtunnel --port 8501
```

### Option 2: Streamlit Cloud

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main

# 2. Go to share.streamlit.io and deploy
```

---

## 🔒 Security Considerations

### For Public Deployment:

1. **Add Authentication:**
```python
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == "your_password":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # Your app code here
    st.write("Welcome to the CRM!")
```

2. **Environment Variables:**
   - Never commit API keys or passwords
   - Use `.env` files locally
   - Use platform environment variables in production

3. **Rate Limiting:**
   - Add rate limiting to prevent abuse
   - Use Cloudflare for DDoS protection (free)

---

## 🆘 Troubleshooting

### Issue: "Module not found"
```bash
pip install -r requirements.txt
```

### Issue: "Port already in use"
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

### Issue: "Database connection failed"
- Check your DATABASE_URL environment variable
- Verify Supabase credentials
- Check firewall settings

---

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Render Docs:** https://render.com/docs
- **Supabase Docs:** https://supabase.com/docs
- **ngrok Docs:** https://ngrok.com/docs

---

## 🎉 Next Steps

1. Choose your deployment method
2. Follow the step-by-step guide
3. Test your deployment
4. Share the URL with users!

**Need help?** Check the troubleshooting section or open an issue on GitHub.

---

**Created by:** Satyajeet Singh Rathod  
**Project:** Intelligent CRM & Lead Generation Platform  
**Last Updated:** January 2026
