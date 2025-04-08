from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from routes import user_routes, auth_routes
from services.auth_service import get_current_user
from models.user import User
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

app = FastAPI()

# Security middleware
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.bancoseguro.com", "localhost"]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.bancoseguro.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-ID"]
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Include routers with rate limits
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(user_routes.router, prefix="/api", tags=["ai"])

@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    return {
        "message": "API de plataforma bancaria segura",
        "security": {
            "version": "1.0",
            "compliance": "PCI-DSS 4.0"
        }
    }

@app.get("/protected")
@limiter.limit("30/minute")
async def protected_route(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Protected route",
        "user": current_user.email[:2] + "*****@****",  # Mask email
        "access": "authenticated"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "security": "enabled"}
