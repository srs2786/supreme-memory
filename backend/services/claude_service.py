import json
import os
from openai import OpenAI
from backend.config import get_config
from backend.utils.retry import retry_with_backoff

MODEL = "anthropic/claude-sonnet-4-5"  # OpenRouter model ID — change if needed

def get_client():
    cfg = get_config()
    return OpenAI(
        api_key=cfg["openrouter_api_key"],
        base_url="https://openrouter.ai/api/v1",
        timeout=60.0,
    )

def load_style_guide() -> dict:
    with open("config/style_guide.json") as f:
        return json.load(f)

def _chat(client, prompt: str, max_tokens: int, temperature: float = 0.9) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

@retry_with_backoff(max_retries=3)
def suggest_topics(sources_context: str, existing_topics: list[str]) -> list[str]:
    """Generate 5 fresh topic suggestions avoiding duplicates."""
    client = get_client()
    style = load_style_guide()
    existing_str = "\n".join(existing_topics) if existing_topics else "None yet"

    prompt = f"""You are generating LinkedIn post topics for {style['author']['name']},
a {style['author']['title']}.

Voice: {style['voice']['tone']}
Avoid: {', '.join(style['voice']['avoid'])}
Prefer: {', '.join(style['voice']['prefer'])}

Recent source headlines for inspiration:
{sources_context}

Already posted topics (DO NOT repeat these angles):
{existing_str}

Generate exactly 5 fresh topic ideas. Each should be a specific insight or
counterintuitive observation a plant manager or COO would stop scrolling for.
Not generic titles — phrased as an insight or tension.

IMPORTANT: Every time you are called, generate DIFFERENT topics. Explore different angles:
factory floor operations, supplier dynamics, workforce/shift issues, equipment ROI,
ERP/WMS failures, quality escapes, energy costs, inventory traps, lean myths, etc.
Do not default to the same themes each time. Be unpredictable and varied.
Random seed: {__import__('random').randint(1, 999999)}

Return ONLY a JSON array of 5 strings. No preamble, no markdown.
Example: ["Topic one", "Topic two", "Topic three", "Topic four", "Topic five"]"""

    return json.loads(_chat(client, prompt, 500))

@retry_with_backoff(max_retries=3)
def draft_post(topic: str, user_details: str = "") -> dict:
    """Draft a full post — caption, headline, sections, hashtags."""
    client = get_client()
    style = load_style_guide()

    prompt = f"""You are writing a LinkedIn post for {style['author']['name']},
a {style['author']['title']}.

Voice: {style['voice']['tone']}
Avoid: {', '.join(style['voice']['avoid'])}
Rules: {'; '.join(style['rules'])}

Topic: {topic}
{f"Additional context from user: {user_details}" if user_details else ""}

Write the following and return ONLY valid JSON, no markdown, no preamble:

{{
  "headline": "10-15 word insight that works as a standalone screenshot",
  "caption": "150-250 word caption. Sharp opening. Real specifics. Closing question.",
  "sections": [
    {{"number": "01", "title": "6-10 word bold point", "body": "2 sentences max, specific and mechanistic"}},
    {{"number": "02", "title": "6-10 word bold point", "body": "2 sentences max, specific and mechanistic"}},
    {{"number": "03", "title": "6-10 word bold point", "body": "2 sentences max, specific and mechanistic"}}
  ],
  "hashtags": ["8 to 12 hashtags from the brand list"]
}}"""

    return json.loads(_chat(client, prompt, 1200))

@retry_with_backoff(max_retries=3)
def improve_post(original: dict, feedback: str) -> dict:
    """Regenerate post incorporating user feedback."""
    client = get_client()
    style = load_style_guide()

    prompt = f"""You are improving a LinkedIn post for {style['author']['name']}.

Original post:
{json.dumps(original, indent=2)}

User feedback:
{feedback}

IMPORTANT: Apply the feedback precisely and make VISIBLE changes. If the feedback mentions the headline/heading, you MUST write a completely different headline — do not keep any part of the original headline. The user must be able to see a clear difference.
Voice rules still apply: {style['voice']['tone']}

Return ONLY valid JSON in the exact same structure as the original. No markdown."""

    return json.loads(_chat(client, prompt, 1200))
