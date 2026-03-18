# Content Pipeline

Semi-automated LinkedIn content pipeline with human-in-the-loop review dashboard.

## Setup

1. Copy `.env.example` to `.env` and fill in all values
2. Add your headshot to `assets/headshots/head_shot.jpg`
3. Run Supabase SQL migrations (see CLAUDE.md Step 4)
4. Install dependencies: `pip install -r requirements.txt`
5. Test locally: `uvicorn backend.main:app --reload`
6. Health check: http://localhost:8000/health

## Frontend Config

Update these in `frontend/app.js`:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `API_BASE` (your Railway URL)

## Deployment

Push to GitHub — Railway auto-deploys on push.
