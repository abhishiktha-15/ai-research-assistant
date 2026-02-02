# 🚀 GitHub Push Instructions

## Quick Steps to Push to GitHub

### 1. Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click the **"+"** icon in top right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `RAG2` (or `ai-research-assistant`)
   - **Description**: "AI Research Paper Assistant with RAG - Upload PDFs and ask questions"
   - **Visibility**: Public (recommended) or Private
   - ⚠️ **DO NOT** check "Initialize this repository with a README"
4. Click **"Create repository"**

### 2. Push Your Code

GitHub will show you commands. Use these instead:

```bash
# Navigate to your project
cd E:\PROJECTS\RAG2

# Add GitHub as remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/RAG2.git

# Rename branch to main
git branch -M main

# Push code to GitHub
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/RAG2.git
git branch -M main
git push -u origin main
```

### 3. Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files:
   - ✅ frontend/
   - ✅ src/
   - ✅ app.py
   - ✅ README.md
   - ✅ LICENSE
   - ✅ etc.

---

## 🌐 Next: Deploy Your App

### Deploy Backend (Render)

1. Go to [render.com](https://render.com) → Sign up
2. Dashboard → **"New +"** → **"Web Service"**
3. **"Connect account"** → Authorize GitHub
4. Select your **RAG2** repository
5. Configure:
   - **Name**: `rag2-backend`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && pip install -r requirements-api.txt
     ```
   - **Start Command**: 
     ```
     uvicorn app:app --host 0.0.0.0 --port $PORT
     ```
6. Click **"Environment"** → Add variables:
   - `GEMINI_API_KEY` = your API key
   - `ENDEE_HOST` = `localhost`
   - `ENDEE_PORT` = `8000`
   - `EMBEDDING_MODEL` = `sentence-transformers`
   - `LLM_PROVIDER` = `gemini`
   - `LLM_MODEL` = `gemini-2.5-flash`
7. Click **"Create Web Service"**
8. Wait 5-10 minutes for deployment
9. Copy your backend URL (e.g., `https://rag2-backend.onrender.com`)

### Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. Dashboard → **"Add New..."** → **"Project"**
3. **"Import Git Repository"** → Select **RAG2**
4. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
5. Click **"Environment Variables"** → Add:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://rag2-backend.onrender.com` (your Render URL)
6. Click **"Deploy"**
7. Wait 2-3 minutes
8. Visit your live app! 🎉

---

## ✅ Post-Deployment

### Update README with Live Links

Edit your README.md and add at the top:

```markdown
## 🌐 Live Demo

**Try it now:** https://your-app.vercel.app

- **Frontend**: https://your-app.vercel.app
- **API**: https://rag2-backend.onrender.com
- **API Docs**: https://rag2-backend.onrender.com/docs
```

Commit and push:
```bash
git add README.md
git commit -m "Add live demo links"
git push
```

---

## 🔍 Troubleshooting

### "Remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/RAG2.git
```

### "Authentication failed"
- Use GitHub Personal Access Token instead of password
- Go to GitHub → Settings → Developer settings → Personal access tokens
- Generate new token with `repo` scope
- Use token as password when pushing

### Backend deployment fails
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure build command is correct

### Frontend can't connect to API
- Check CORS settings in backend
- Verify `VITE_API_URL` matches your Render URL exactly
- Check browser console for errors

---

## 📧 Share Your Project

Once deployed, share:
- GitHub repo: `https://github.com/YOUR_USERNAME/RAG2`
- Live demo: `https://your-app.vercel.app`

**Add badges to README:**
```markdown
![Live Demo](https://img.shields.io/badge/demo-live-success)
![GitHub](https://img.shields.io/github/stars/YOUR_USERNAME/RAG2?style=social)
```

---

**Good luck with your deployment! 🚀**
