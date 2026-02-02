# Deployment Instructions

## Quick Start - Local Development

### Backend

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-api.txt
   ```

2. **Configure environment:**
   ```bash
   copy .env.example .env
   # Add your GEMINI_API_KEY to .env
   ```

3. **Start Endee (vector database):**
   ```bash
   docker-compose up -d
   ```

4. **Run the API server:**
   ```bash
   python app.py
   ```
   API will be available at `http://localhost:8000`

### Frontend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173`

---

## Deployment to Production

### Option 1: Vercel (Frontend) + Render (Backend)

#### Deploy Backend to Render

1. Create account on [Render](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `rag2-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && pip install -r requirements-api.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `GEMINI_API_KEY`
   - `ENDEE_HOST=localhost`
   - `ENDEE_PORT=8000`
   - `ALLOWED_ORIGINS=https://your-frontend.vercel.app`
6. Deploy!

#### Deploy Frontend to Vercel

1. Create account on [Vercel](https://vercel.com)
2. Click "New Project" → Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variable:
   - `VITE_API_URL` = `https://your-backend.onrender.com`
5. Deploy!

### Option 2: Deploy Both on Render

1. Follow backend deployment steps above
2. Add build command for frontend:
   ```bash
   cd frontend && npm install && npm run build && cd ..
   ```
3. Modify `app.py` to serve static files

### Option 3: Heroku

Similar to Render, but uses `Procfile`:

```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

## Environment Variables Summary

**Backend (.env):**
```env
GEMINI_API_KEY=your_key_here
ENDEE_HOST=localhost
ENDEE_PORT=8000
EMBEDDING_MODEL=sentence-transformers
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
ALLOWED_ORIGINS=*
```

**Frontend (.env.production):**
```env
VITE_API_URL=https://your-backend-url.com
```

---

## Troubleshooting

### Backend won't start
- Check if port 8000 is in use
- Verify all dependencies are installed
- Check `.env` file exists with valid API keys

### Frontend can't connect to API
- Verify backend is running
- Check CORS settings in `app.py`
- Update `VITE_API_URL` environment variable

### Papers not uploading
- Ensure `data/papers/` directory exists
- Check file size limits (default 100MB)
- Verify Endee is running

---

## Production Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured
- [ ] CORS properly set
- [ ] API endpoints tested
- [ ] Upload functionality tested
- [ ] Query functionality tested
- [ ] Error handling works
- [ ] Mobile responsive
- [ ] SSL/HTTPS enabled

---

**Need help?** Check the main [README.md](./README.md) for more information.
