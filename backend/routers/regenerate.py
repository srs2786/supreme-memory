from fastapi import APIRouter, HTTPException
from backend.models.schemas import RegenerateRequest
from backend.services.claude_service import improve_post
from backend.services.card_generator import render_card
from backend.services.supabase_service import save_draft

router = APIRouter()

@router.post("/regenerate")
async def regenerate_post(req: RegenerateRequest):
    """Improve existing draft using user feedback."""
    try:
        # Improve with Claude
        improved = improve_post(req.original_draft, req.feedback)

        # Re-render card
        card_path = render_card(improved, req.topic_slug)

        # Save new iteration
        saved = save_draft({
            "topic_slug": req.topic_slug,
            "caption": improved["caption"],
            "headline": improved["headline"],
            "sections": improved["sections"],
            "hashtags": improved["hashtags"],
            "card_path": card_path,
            "feedback": req.feedback,
            "status": "pending"
        })

        return {
            "draft_id": saved["id"],
            "topic_slug": req.topic_slug,
            "draft": improved,
            "card_path": card_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
