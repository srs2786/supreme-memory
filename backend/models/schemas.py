from pydantic import BaseModel
from typing import Optional

class TopicRequest(BaseModel):
    mode: str  # "suggest" or "custom"
    topic: Optional[str] = None
    details: Optional[str] = None
    tone: Optional[str] = None
    audience: Optional[str] = None

class GenerateRequest(BaseModel):
    topic: str
    details: Optional[str] = ""

class RegenerateRequest(BaseModel):
    draft_id: str
    topic_slug: str
    original_draft: dict
    feedback: str

class PublishRequest(BaseModel):
    draft_id: str
    topic_slug: str
    draft: dict
    card_path: str
