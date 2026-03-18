import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.config import get_config
from backend.routers import topics, generate, regenerate, publish

# Validate env vars at startup
try:
    cfg = get_config()
except EnvironmentError as e:
    print(f"[Startup] CONFIGURATION ERROR: {e}")
    raise

app = FastAPI(title="Content Pipeline API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[cfg["frontend_url"], "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(regenerate.router, prefix="/api")
app.include_router(publish.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/debug/fonts")
async def debug_fonts():
    import glob, subprocess
    results = {}
    # Check known paths
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    results["known_paths"] = {p: os.path.exists(p) for p in paths}
    # Find DejaVu anywhere
    results["nix_search"] = glob.glob("/nix/store/*/share/fonts/truetype/DejaVuSans.ttf")[:3]
    results["usr_share_dejavu"] = glob.glob("/usr/share/fonts/truetype/dejavu/*.ttf")
    # Test PIL font loading
    from PIL import ImageFont
    for path in paths:
        if os.path.exists(path):
            try:
                ImageFont.truetype(path, 40)
                results[f"pil_{path}"] = "OK"
            except Exception as e:
                results[f"pil_{path}"] = str(e)
    return results

@app.get("/card/{slug}")
async def serve_card(slug: str):
    path = f"output/linkedin/{slug}/post.jpg"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Card not found")
    return FileResponse(path, media_type="image/jpeg")
