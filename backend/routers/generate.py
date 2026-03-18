import re
from fastapi import APIRouter, HTTPException
from backend.models.schemas import GenerateRequest
from backend.services.claude_service import draft_post
from backend.services.card_generator import render_card
from backend.services.supabase_service import log_topic, save_draft, is_duplicate

router = APIRouter()

@router.post("/generate")
async def generate_post(req: GenerateRequest):
    """Draft post + render card for a given topic."""
    try:
        # Dedup check
        if is_duplicate(req.topic):
            raise HTTPException(status_code=409,
                detail="This topic has already been posted. Please choose a different angle.")

        # Generate slug
        slug = re.sub(r"[^a-z0-9]+", "-", req.topic.lower()).strip("-")[:60]

        # Draft content
        draft = draft_post(req.topic, req.details or "")

        # Render card
        card_path = render_card(draft, slug)

        # Log to Supabase
        log_topic(req.topic, slug)
        saved = save_draft({
            "topic_slug": slug,
            "caption": draft["caption"],
            "headline": draft["headline"],
            "sections": draft["sections"],
            "hashtags": draft["hashtags"],
            "card_path": card_path,
            "iteration": 1,
            "status": "pending"
        })

        return {
            "draft_id": saved["id"],
            "topic_slug": slug,
            "draft": draft,
            "card_path": card_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
