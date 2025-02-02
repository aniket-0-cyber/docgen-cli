from typing import List

class URLConfig:
    # Base URLs for AI servers
    SERVER_URLS: List[str] = [
        "http://147.182.206.42:8000",
        "http://147.182.206.42:8001",
        "http://147.182.206.16:8002",
        "http://147.182.206.16:8003",
    ]
    
    # Usage and auth endpoints
    USAGE_BASE_URL: str = f"{SERVER_URLS[0]}/api/v1/usage"
    AUTH_BASE_URL: str = f"{SERVER_URLS[2]}/api/v1/auth"
    
    # Specific endpoints
    USAGE_CHECK_URL: str = f"{USAGE_BASE_URL}/check"
    USAGE_TRACK_URL: str = f"{USAGE_BASE_URL}/track"
    AUTH_VERIFY_URL: str = f"{AUTH_BASE_URL}/verify-key"
    GENERATE_URL: str = "/api/v1/gemini/generate"
    GENERATE_BATCH_URL: str = "/api/v1/gemini/generate/batch" 