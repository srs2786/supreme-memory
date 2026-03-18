import os
from dotenv import load_dotenv

load_dotenv()

def get_config():
    required = [
        "OPENROUTER_API_KEY",
        "LINKEDIN_ACCESS_TOKEN",
        "LINKEDIN_PERSON_URN",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Check your .env file or Railway environment settings."
        )
    return {
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "linkedin_token": os.getenv("LINKEDIN_ACCESS_TOKEN"),
        "linkedin_urn": os.getenv("LINKEDIN_PERSON_URN"),
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_key": os.getenv("SUPABASE_SERVICE_KEY"),
        "frontend_url": os.getenv("FRONTEND_URL", "*"),
        "secret_key": os.getenv("SECRET_KEY", "dev-secret"),
    }
