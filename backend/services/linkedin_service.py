import httpx
from backend.config import get_config
from backend.utils.retry import retry_with_backoff

@retry_with_backoff(max_retries=3)
def post_to_linkedin(draft: dict, card_path: str) -> dict:
    """Upload card and create LinkedIn post. Returns result dict."""
    cfg = get_config()
    token = cfg["linkedin_token"]
    urn = cfg["linkedin_urn"]
    author = f"urn:li:person:{urn}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 1 — Register upload
    reg_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    reg = httpx.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        json=reg_payload, headers=headers, timeout=15
    )
    if reg.status_code != 200:
        raise RuntimeError(f"LinkedIn register upload failed: {reg.status_code} {reg.text}")

    upload_url = reg.json()["value"]["uploadMechanism"] \
        ["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = reg.json()["value"]["asset"]

    # Step 2 — Upload JPEG
    with open(card_path, "rb") as f:
        image_data = f.read()
    upload_resp = httpx.put(
        upload_url,
        content=image_data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"},
        timeout=30
    )
    if upload_resp.status_code not in (200, 201):
        raise RuntimeError(f"LinkedIn image upload failed: {upload_resp.status_code} {upload_resp.text}")

    # Step 3 — Create post
    caption_text = draft["caption"] + "\n\n" + " ".join(draft.get("hashtags", []))
    post_payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": caption_text},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "media": asset,
                    "title": {"text": draft["headline"]}
                }]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    post_resp = httpx.post(
        "https://api.linkedin.com/v2/ugcPosts",
        json=post_payload, headers=headers, timeout=15
    )
    if post_resp.status_code != 201:
        raise RuntimeError(f"LinkedIn post failed: {post_resp.status_code} {post_resp.text}")

    return {"success": True, "post_id": post_resp.headers.get("x-restli-id", "")}
