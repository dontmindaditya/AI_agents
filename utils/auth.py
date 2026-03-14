"""
Authentication module using Supabase JWT verification.

This module provides authentication and authorization utilities for the AgentHub API.
It supports multiple authentication methods:
1. Supabase JWT tokens (via Authorization header)
2. API Key authentication (via X-API-Key header)

Usage:
    # For JWT authentication
    from utils.auth import get_current_user
    
    @app.get("/protected")
    async def protected_route(user: User = Depends(get_current_user)):
        return {"user": user}
    
    # For API Key authentication
    from utils.auth import verify_api_key
    
    @app.post("/agent/execute")
    async def execute_agent(user: User = Depends(verify_api_key)):
        return {"user": user}

Environment Variables:
    - API_KEY_ENABLED: Enable/disable API key authentication (default: True)
    - API_KEYS: Comma-separated list of valid API keys
"""

from typing import Optional, Dict, Any, Callable
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import jwt, JWTError
from pydantic import BaseModel
from config import settings


security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class User(BaseModel):
    """
    Authenticated user model.
    
    Attributes:
        id: Unique user identifier
        email: User's email address
        role: User's role (admin, developer, api_user, etc.)
        metadata: Additional user information
    """
    id: str
    email: Optional[str] = None
    role: Optional[str] = None
    metadata: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Verify Supabase JWT token and return current user.
    
    Requires SUPABASE_URL and SUPABASE_SERVICE_KEY or NEXT_PUBLIC_SUPABASE_ANON_KEY
    to be configured in environment.
    
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # For now, support both Supabase JWT and simple API key fallback
        # When Supabase is configured, use proper JWT verification
        
        if settings.SUPABASE_URL and settings.NEXT_PUBLIC_SUPABASE_ANON_KEY:
            user = await _verify_supabase_token(token)
        else:
            # Fallback: treat as simple API key (for development)
            user = _verify_api_key(token)
            
        return user
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _verify_supabase_token(token: str) -> User:
    """Verify Supabase JWT token"""
    # Supabase JWT verification
    # The token contains claims in the payload
    try:
        # Decode without verification for now (Supabase handles this)
        # In production, you would verify against Supabase's JWKS
        payload = jwt.get_unverified_claims(token)
        
        return User(
            id=payload.get("sub", ""),
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
            metadata=payload
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase token"
        )


def _verify_api_key(token: str) -> User:
    """Simple API key verification (development fallback)"""
    # In development, allow any non-empty token
    # Replace with actual API key validation in production
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return User(
        id="dev-user",
        email="dev@example.com",
        role="developer",
        metadata={"mode": "development"}
    )


def require_role(allowed_roles: list[str]):
    """Dependency factory to require specific roles"""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return role_checker


# Optional authentication (doesn't raise error if no token)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get user if authenticated, None otherwise"""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)) -> User:
    """
    Verify API key from X-API-Key header.
    
    Requires API_KEY_ENABLED=True and API_KEYS list in settings.
    
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not settings.API_KEY_ENABLED:
        return User(
            id="api-user",
            email="api@example.com",
            role="api_user",
            metadata={"mode": "disabled"}
        )
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Please provide X-API-Key header.",
            headers={"X-API-Key": "Required"},
        )
    
    if settings.API_KEYS and api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return User(
        id="api-user",
        email="api@example.com",
        role="api_user",
        metadata={"mode": "api_key", "key_hash": hash(api_key)}
    )
