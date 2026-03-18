from fastapi import APIRouter, HTTPException
from backend.models.schemas import PublishRequest
from backend.services.linkedin_service import post_to_linkedin
from backend.services.supabase_service import mark_published

router = APIRouter()

LINKEDIN_ENABLED = False  # Set to True when ready to go live

@router.post("/publish")
async def publish_post(req: PublishRequest):
    """Post to LinkedIn and mark as published in Supabase."""
    try:
        if LINKEDIN_ENABLED:
            result = post_to_linkedin(req.draft, req.card_path)
            linkedin_post_id = result.get("post_id", "")
        else:
            print("[Publish] LinkedIn posting disabled — test mode")
            linkedin_post_id = "test-mode"

        mark_published(req.topic_slug, req.draft_id)
        return {"success": True, "linkedin_post_id": linkedin_post_id, "test_mode": not LINKEDIN_ENABLED}
    except Exception as e:
        raise HTTPException(status_code=500,
            detail=f"Publishing failed — your draft is saved and can be retried. Error: {str(e)}")
