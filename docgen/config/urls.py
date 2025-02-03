from typing import List

class URLConfig:
    # Base URLs for AI servers
    SERVER_URLS: List[str] = [
        "https://api1.docgen.dev",
        "https://api2.docgen.dev",
    ]
    
    # Usage and auth endpoints
    USAGE_BASE_URL: str = f"{SERVER_URLS[0]}/api/v1/usage"
    AUTH_BASE_URL: str = f"{SERVER_URLS[1]}/api/v1/auth"
    
    # Specific endpoints
    USAGE_CHECK_URL: str = f"{USAGE_BASE_URL}/check"
    USAGE_TRACK_URL: str = f"{USAGE_BASE_URL}/track"
    AUTH_VERIFY_URL: str = f"{AUTH_BASE_URL}/verify-key"
    GENERATE_URL: str = "/api/v1/gemini/generate"
    GENERATE_BATCH_URL: str = "/api/v1/gemini/generate/batch" 