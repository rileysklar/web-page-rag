"""
Security utilities for the API.
"""
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from request header
        
    Returns:
        str: Verified API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if api_key == settings.API_KEY:
        return api_key
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API Key"
    ) 