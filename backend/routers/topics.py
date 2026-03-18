from fastapi import APIRouter, HTTPException
from backend.services.sources import gather_all_sources
from backend.services.claude_service import suggest_topics
from backend.services.supabase_service import get_client

router = APIRouter()

@router.get("/topics")
async def get_topic_suggestions():
    """Gather sources, check dedup, return 5 fresh topic suggestions."""
    try:
        # Get already posted topics
        client = get_client()
        result = client.table("topics_log").select("topic") \
            .eq("status", "published").execute()
        existing = [r["topic"] for r in result.data]

        # Gather sources
        sources = gather_all_sources()

        # Generate suggestions
        topics = suggest_topics(sources, existing)
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
