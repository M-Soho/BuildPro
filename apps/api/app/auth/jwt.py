from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional, Dict, Any
from app.core.config import settings
from app.models.user import UserRole
import requests

security = HTTPBearer()


class ClerkAuth:
    """Clerk JWT validation"""
    
    def __init__(self):
        self.jwks_url = settings.CLERK_JWKS_URL
        self._jwks_cache: Optional[Dict[str, Any]] = None
    
    def get_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Clerk"""
        if not self._jwks_cache:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            self._jwks_cache = response.json()
        return self._jwks_cache
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Clerk JWT and return claims"""
        try:
            # For MVP, we'll use the PEM key if provided
            if settings.CLERK_PEM_PUBLIC_KEY:
                payload = jwt.decode(
                    token,
                    settings.CLERK_PEM_PUBLIC_KEY,
                    algorithms=["RS256"],
                )
                return payload
            else:
                raise ValueError("CLERK_PEM_PUBLIC_KEY not configured")
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )


clerk_auth = ClerkAuth()


async def get_current_user_from_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Dependency to extract and validate JWT, then set user context on request.state
    """
    token = credentials.credentials
    
    try:
        # Verify token and get claims
        claims = clerk_auth.verify_token(token)
        
        # Extract user info from claims
        user_id = claims.get("sub")  # Clerk user ID
        
        # Extract custom claims (set in Clerk)
        tenant_id = claims.get("tenant_id")
        user_role = claims.get("role", "SUB")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token",
            )
        
        # Set context on request state
        request.state.user_id = user_id
        request.state.tenant_id = tenant_id
        request.state.user_role = user_role
        request.state.auth_claims = claims
        
        return claims
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional: Supabase Auth alternative
class SupabaseAuth:
    """Supabase JWT validation"""
    
    def __init__(self):
        self.jwt_secret = settings.SUPABASE_JWT_SECRET
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Supabase JWT and return claims"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
