from supabase import create_client
from backend.config import get_config

def get_client():
    cfg = get_config()
    return create_client(cfg["supabase_url"], cfg["supabase_key"])

def is_duplicate(topic: str) -> bool:
    """Check if topic has already been posted."""
    try:
        client = get_client()
        result = client.table("topics_log") \
            .select("id") \
            .ilike("topic", f"%{topic}%") \
            .eq("status", "published") \
            .execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"[Supabase] Dedup check failed: {e}")
        raise

def log_topic(topic: str, slug: str) -> dict:
    """Log a new topic as pending."""
    try:
        client = get_client()
        result = client.table("topics_log") \
            .insert({"topic": topic, "slug": slug, "status": "pending"}) \
            .execute()
        return result.data[0]
    except Exception as e:
        print(f"[Supabase] Topic log failed: {e}")
        raise

def save_draft(draft: dict) -> dict:
    """Save a post draft."""
    try:
        client = get_client()
        result = client.table("post_drafts").insert(draft).execute()
        return result.data[0]
    except Exception as e:
        print(f"[Supabase] Draft save failed: {e}")
        raise

def mark_published(slug: str, draft_id: str):
    """Mark topic and draft as published."""
    try:
        client = get_client()
        client.table("topics_log") \
            .update({"status": "published", "posted_at": "now()"}) \
            .eq("slug", slug).execute()
        client.table("post_drafts") \
            .update({"status": "published"}) \
            .eq("id", draft_id).execute()
    except Exception as e:
        print(f"[Supabase] Mark published failed: {e}")
        raise
