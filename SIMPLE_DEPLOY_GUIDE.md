# 🚀 Simple Deployment Guide - Click by Click

## Part 1: Deploy Frontend (Vercel) - 5 minutes

### Step 1: Go to Vercel
1. Open your browser
2. Go to: **https://vercel.com**
3. Click the **"Sign Up"** button (top right)

### Step 2: Connect GitHub
1. Click **"Continue with GitHub"**
2. It will ask for permission to access your repos
3. Click **"Authorize Vercel"**

### Step 3: Import Your Project
1. You'll see the Vercel dashboard
2. Click **"Add New..."** → **"Project"**
3. Find **"ai-research-assistant"** in the list
4. Click **"Import"** next to it

### Step 4: Configure (IMPORTANT)
1. **Root Directory**: Click "Edit" → Type `frontend` → Click outside to save
2. **Framework Preset**: Should say "Vite" (auto-detected) ✓
3. **Build Command**: Should say `npm run build` ✓
4. **Output Directory**: Should say `dist` ✓

### Step 5: Skip Environment Variables for Now
1. Click **"Deploy"** button (big blue button at bottom)
2. Wait 2-3 minutes (you'll see progress)
3. When done, you'll see 🎉 Congratulations!

### Step 6: Copy Your Frontend URL
1. You'll see something like: `https://ai-research-assistant-abc123.vercel.app`
2. **COPY THIS URL** - you'll need it in the next step!

---

## Part 2: Deploy Backend (Render) - 7 minutes

### Step 1: Go to Render
1. Open new tab
2. Go to: **https://render.com**
3. Click **"Get Started"** or **"Sign Up"**

### Step 2: Connect GitHub
1. Click **"GitHub"** button
2. Authorize Render to access your repos
3. Click **"Authorize Render"**

### Step 3: Create Web Service
1. In Render dashboard, click **"New +"** (top right)
2. Select **"Web Service"**
3. Find **"ai-research-assistant"** in the repo list
4. Click **"Connect"**

### Step 4: Configure Backend (Copy these exactly)

**Fill in these fields:**

| Field | Value |
|-------|-------|
| **Name** | `ai-research-backend` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && pip install -r requirements-api.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

### Step 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these **one by one** (click "+ Add Environment Variable" for each):

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | Your API key from .env file |
| `ENDEE_HOST` | `localhost` |
| `ENDEE_PORT` | `8000` |
| `EMBEDDING_MODEL` | `sentence-transformers` |
| `SENTENCE_TRANSFORMER_MODEL` | `all-MiniLM-L6-v2` |
| `LLM_PROVIDER` | `gemini` |
| `LLM_MODEL` | `gemini-2.5-flash` |
| `CHUNK_SIZE` | `500` |
| `CHUNK_OVERLAP` | `50` |
| `TOP_K` | `5` |
| `SIMILARITY_THRESHOLD` | `0.7` |
| `ALLOWED_ORIGINS` | `*` |

### Step 6: Deploy!
1. Scroll down
2. Click **"Create Web Service"** (big button)
3. Wait 5-10 minutes (Render takes longer than Vercel)
4. When you see "Live" with a green dot, it's ready!

### Step 7: Copy Backend URL
1. At the top, you'll see: `https://ai-research-backend-xyz.onrender.com`
2. **COPY THIS URL**

---

## Part 3: Connect Frontend to Backend - 2 minutes

### Go Back to Vercel
1. Open Vercel tab (or go to vercel.com)
2. Click on your **"ai-research-assistant"** project
3. Click **"Settings"** tab
4. Click **"Environment Variables"** in sidebar

### Add Backend URL
1. Click **"Add"**
2. **Key**: `VITE_API_URL`
3. **Value**: YOUR BACKEND URL (the Render URL you copied)
   - Example: `https://ai-research-backend-xyz.onrender.com`
4. Click **"Save"**

### Redeploy
1. Go to **"Deployments"** tab
2. Click the three dots (...) on the latest deployment
3. Click **"Redeploy"**
4. Wait 2 minutes

---

## 🎉 YOU'RE DONE!

### Test Your App
1. Go to your frontend URL: `https://ai-research-assistant-abc123.vercel.app`
2. You should see your beautiful app!
3. Try uploading a PDF
4. Try asking a question!

---

## 📍 Your Live URLs

**Frontend (User Interface):**
```
https://your-vercel-url.vercel.app
```

**Backend (API):**
```
https://your-backend.onrender.com
```

**API Documentation:**
```
https://your-backend.onrender.com/docs
```

---

## ⚠️ Troubleshooting

### "Cannot connect to API"
- Wait 1-2 minutes after backend deployment
- Check that `VITE_API_URL` is set correctly in Vercel
- Make sure you redeployed after adding the variable

### Backend deployment fails
- Check all environment variables are added
- Verify build command is exactly: `pip install -r requirements.txt && pip install -r requirements-api.txt`
- Check logs in Render dashboard

### Papers won't upload
- First deployment might be slow (Render free tier)
- Wait a few minutes for backend to wake up
- Check browser console (F12) for errors

---

## 💡 Tips

- **Render free tier**: First request after 15 mins of inactivity takes ~30 seconds (cold start)
- **Vercel**: Updates automatically when you push to GitHub!
- **Render**: Auto-deploys on git push too!

---

**Total Time: ~15 minutes**

Good luck! 🚀
