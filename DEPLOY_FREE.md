# How to Go Live (Free)

Since your project uses a **Local Database (SQLite)** and **n8n Automation**, the best way to share it for free without losing data is using a **Tunnel**.

## 🚀 Recommended Method: LocalTunnel

This creates a public URL (like `https://your-name.loca.lt`) that points to your Mac.

### 1. Start your App (If not running)
Make sure your app is running in your terminal:
```bash
npm start
streamlit run app.py
```

### 2. Create the Public Link
Open a **new terminal** and run:
```bash
npx localtunnel --port 8501
```

It will give you a URL like `https://shiny-pugs-jump.loca.lt`.
**Share this URL** with anyone. They can access your dashboard as long as your script is running.

---

## ☁️ Permanent Cloud Hosting (Advanced)
If you want to host it permanently (so it works when your laptop is off), you must change your technology stack because free cloud servers **delete files (SQLite)** when they restart.

1. **Database**: Switch from SQLite to **Supabase** (Free Postgres).
2. **Backend**: Host code on **Render.com** (Free Web Service).
3.  **Frontend**: Host `app.py` on **Streamlit Community Cloud** (Free).
    *   Connect your GitHub Repo.
    *   Set Environment Variable `BACKEND_URL` to your Render Backend URL.

*Note: This requires rewriting `database.js` to use Postgres instead of SQLite.*
